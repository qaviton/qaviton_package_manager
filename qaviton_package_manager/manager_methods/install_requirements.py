# Copyright 2019 qaviton.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# https://github.com/qaviton/qaviton_package_manager/blob/master/LICENSE
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

from typing import Dict
from os import sep, listdir
from pkginfo import get_metadata
from tempfile import TemporaryDirectory
from qaviton_pip import pip
from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation
from qaviton_package_manager.utils.functions import package_match
from qaviton_package_manager.utils.logger import log
from qaviton_processes import run
from sys import executable
from qaviton_git import Git


class Package:
    def __init__(self, **kwargs):
        self._attr = {}
        self.link: str = None
        self.url: str = None
        self.branch: str = None
        self.vcs: str = None
        self.protocol: str = None
        self.version: str = None
        self.versions: [str] = None
        self.name: str = None
        self.parent: str = None
        self.path: str = None
        for attr, value \
        in kwargs.items():
            self[attr] = value

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setattr__(self, key, value):
        object.__setattr__(self, key, value)
        self._attr[key] = value


class PackageManager:
    installed = None
    git = None

    @classmethod
    def init(cls, git: Git, packages: [str]):
        cls.installed = pip('freeze').decode('utf-8').splitlines()
        cls.git = git
        return cls(packages)

    def __init__(self, packages: [str]):
        self.packages = packages
        self.vcs_packages: Dict[str, Package] = {}

        for pkg in packages: self.create_package_dict(pkg)
        if self.vcs_packages: self.pip_packages = [pkg for pkg in self.packages if 'git+' not in pkg]
        else: self.pip_packages = packages

    def install_vcs(self):
        with TemporaryDirectory() as tmp:
            for name, pkg in self.vcs_packages.items():

                # filter satisfied requirements
                for i in PackageManager.installed:
                    ins, ver = i.split('==')
                    if ins == name.replace('_', '-'):
                        # lines = r.splitlines()
                        # version = None
                        # for line in lines:
                        #     v = b'Version: '
                        #     if line.startswith(v):
                        #         version = line[len(v):]
                        #         break
                        #
                        log.info(f'{i} requirement from {pkg.link} already satisfied')
                        break
                else:
                    # clone repo
                    pkg.path = tmp + sep + name
                    repo = PackageManager.git.clone(
                        path=pkg.path,
                        url=pkg.url,
                        username=PackageManager.git.username,
                        password=PackageManager.git.password,
                        email=PackageManager.git.email)
                    pkg.versions = sorted(repo('tag --merged').decode('utf-8').splitlines())

                    # get version
                    if pkg.version:
                        # TODO: filter out the highest version
                        # version =
                        # repo(f'checkout tags/{version}')
                        pkg.version = pkg.versions[-1]
                    else:
                        pkg.version = pkg.versions[-1]

                    # get requirements
                    try:
                        requirements_path = pkg.path + sep + 'requirements.txt'
                        with open(requirements_path, encoding='utf-8') as f:
                            requirements = f.read().splitlines()

                        # manage sub requirements
                        requirements_manager = PackageManager(list(requirements))
                        if requirements_manager.vcs_packages:
                            requirements_manager.install_vcs()

                            # update requirements (wheel cannot be created otherwise)
                            for requirements_pkg in requirements_manager.vcs_packages.values():
                                for i, requirement in enumerate(requirements):
                                    if requirements_pkg.link == requirement:
                                        requirements[i] = f'{requirements_pkg.name}=={requirements_pkg.version}'
                            requirements.append('')
                            with open(requirements_path, encoding='utf-8', mode='w') as f:
                                f.write('\n'.join(requirements))

                    except FileNotFoundError as e:
                        log.error(e)
                        log.error(f"{pkg.name} from {pkg.link} is missing requirements.txt file")
                        raise FileNotFoundError("")

                    # create wheel
                    run('cd', pkg.path, '&&', executable, 'setup.py bdist_wheel --universal')
                    dist = pkg.path + sep + 'dist'
                    for fn in listdir(dist):
                        if fn.endswith('.whl'):
                            wheel = dist + sep + fn
                            pip.install(wheel)
                            # print(get_metadata(wheel).requires_dist)
                            break

    def get_dependency_tree(self, pkg: dict):
        tree = []
        while pkg.parent:
            tree.append(pkg.parent)
            pkg = self.vcs_packages[pkg.parent]
        return tree

    def create_package_dict(self, uri: str, **kwargs):
        if 'git+' in uri or '#egg=' in uri:
            error = ValueError(
                f"we detected an unsupported vcs installation:{uri}\n"
                "please view the supported vcs formats of pip here:\n"
                "https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support\n\n"
                "out of those, we dont support git://git.example.com/MyProject#egg=MyProject\n"
                "our format is as follows:\n"
                "git+protocol://git.example.com/MyProject.git@{branch}#egg=MyProject:==version\n"
                # ':==1.1.1,1.1.2,!1.1.3,1.1.*,!1.1.*,!1.1,>1.1,<1.1,1.1-1.3,>=1.1,<=1.1,!(1.2-1.3)'
                "we urge you to use https for a secure network transaction.")
            if 'git+' not in uri or '#egg=' not in uri: raise error
            try:
                a = uri.split('git+', 1)
                b = a[1].rsplit('#egg=', 1)
                c = b[0].split('.git@', 1)

                if ':' in b[1]:
                    name, version = b[1].split(':', 1)
                    version = version.split(',')
                else:
                    name, version = b[1], []

                self.vcs_packages[name] = Package(**{
                    'link': uri,
                    'url': c[0] + '.git',
                    'branch': c[1],
                    'vcs': 'git',
                    'protocol': a[1].split(':', 1)[0],
                    'version': version,
                    'versions': [],
                    'name': name,
                    'parent': None,
                    'path': None,
                    **kwargs,
                })
            except:
                raise error


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        packages = self.configure_packages()
        manager = PackageManager.init(self.git, packages)
        if manager.vcs_packages:
            manager.install_vcs()

        if packages:
            pip.install(manager.pip_packages)

            # TODO: fix this, add check for version evaluation
            # if not install_requirements and self.packages:
            #     with open(self.requirements_path) as f:
            #         packages = f.read().splitlines()
            #     for i, package in enumerate(packages):
            #         for added in self.packages:
            #             if added == package:
            #                 packages[i] = None
            #     packages = [pkg for pkg in packages if pkg is not None]
            #     if packages:
            #         with open(self.requirements_path, 'a') as f:
            #             f.write('\n'+'\n'.join(self.packages))
            if self.packages:
                with open(self.requirements_path) as f:
                    requirements = f.readlines()
                for i, line in enumerate(requirements):
                    requirement = line.replace(' ', '').replace('\n', '')
                    for package in self.packages:
                        if package_match(package.replace(' ', ''), requirement):
                            requirements[i] = None
                with open(self.requirements_path, 'w') as f:
                    f.writelines([pkg for pkg in requirements if pkg is not None] + list({'\n'+pkg for pkg in self.packages}))


class InstallTest(TestOperation, Install):
    def run(self): return Install.run(self)
