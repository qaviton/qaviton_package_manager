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

from typing import Dict, List
from os import sep, listdir
from os.path import exists
# from pkginfo import get_metadata
from tempfile import TemporaryDirectory
from qaviton_pip import pip
from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation
from qaviton_package_manager.utils.functions import package_match
from qaviton_package_manager.utils.logger import log
from qaviton_processes import run
from sys import executable
from qaviton_git import Git
from qaviton_package_manager.exceptions import RepositoryMissMatchError


invalid_package_chars = '=,!~<>'
def get_package_name_from_requirement(requirement: str):
    version = None
    for i, c in enumerate(requirement):
        if c in invalid_package_chars:
            name = requirement[:i]
            for i, c in enumerate(requirement, start=i):
                if c not in invalid_package_chars:
                    version = requirement[i:]
                    break
            return name, version


def normalize_package_name(name):
    return name.replace('_', '-').replace('.', '-').lower()


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
        self.normalized_name: str = None
        self.parent: str = None
        self.repo: Git = None
        self.path: str = None
        self.dist_path: str = None
        self.requirements_path: str = None
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

    def get_dependency_tree(self):
        pkg = self
        tree = []
        while pkg.parent:
            pkg = PackageManager.vcs_packages[pkg.parent]
            tree.append(pkg.link)
        return tree

    def set_paths(self, tmp):
        self.path = tmp + sep + self.name
        self.requirements_path = self.path + sep + 'requirements.txt'
        self.dist_path = self.path + sep + 'dist'

    def clone(self):
        self.repo = PackageManager.git.clone(
            path=self.path,
            url=self.url,
            username=PackageManager.git.username,
            password=PackageManager.git.password,
            email=PackageManager.git.email)

    def set_version(self):
        self.versions = sorted(self.repo('tag --merged').decode('utf-8').splitlines())

        # get version
        if self.version:
            # TODO: filter out the highest version
            # version =
            # repo(f'checkout tags/{version}')
            self.version = self.versions[-1]
        else:
            self.version = self.versions[-1]

    def get_requirements(self):
        try:
            with open(self.requirements_path, encoding='utf-8') as f:
                requirements = f.read().splitlines()
            return requirements
        except FileNotFoundError as e:
            log.error(e)
            log.error(f"{self.name} from {self.link} is missing requirements.txt file")
            raise FileNotFoundError("")


class PackageManager:
    installed = {}
    vcs_packages: Dict[str, Package] = {}
    vcs_ord = []
    pip_packages = []
    git: Git
    tmp: str
    _tmp: TemporaryDirectory
    # satisfied = []

    @classmethod
    def init(cls, git: Git, packages: [str]):
        cls.git = git
        for i in pip('freeze').decode('utf-8').splitlines():
            cls.installed.__setitem__(*i.split('=='))
        return cls(packages)

    def __enter__(self):
        PackageManager._tmp = TemporaryDirectory()
        PackageManager.tmp = PackageManager._tmp.name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        PackageManager._tmp.cleanup()

    def __init__(self, packages: [str], parent: str = None):
        self.packages_to_clone: List[Package] = []
        self.parent = parent
        for pkg in packages:
            self.add_package(pkg)

    def clone_packages(self):
        tmp = PackageManager.tmp
        vcs_packages: List[Package] = self.packages_to_clone

        for pkg in vcs_packages:
            pkg.set_paths(tmp)

            if pkg.normalized_name in PackageManager.installed:
                continue

            if exists(pkg.path):
                continue

            # clone repo
            pkg.clone()
            pkg.set_version()

            # get requirements
            requirements = pkg.get_requirements()

            # manage sub requirements
            requirements_manager = PackageManager(requirements)
            if requirements_manager.packages_to_clone:
                requirements_manager.clone_packages()

                # update requirements (wheel cannot be created otherwise)
                for requirements_pkg in requirements_manager.vcs_packages.values():
                    for i, requirement in enumerate(requirements):
                        if requirements_pkg.link == requirement:
                            requirements[i] = f'{requirements_pkg.name}=={requirements_pkg.version}'
                requirements.append('')
                with open(pkg.requirements_path, encoding='utf-8', mode='w') as f:
                    f.write('\n'.join(requirements))

    def add_package(self, uri: str, **kwargs):
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

                pkg = Package(**{
                    'link': uri,
                    'url': c[0] + '.git',
                    'branch': c[1],
                    'vcs': 'git',
                    'protocol': a[1].split(':', 1)[0],
                    'version': version,
                    'versions': [],
                    'name': name,
                    'normalized_name': normalize_package_name(name),
                    'parent': self.parent,
                    'path': None,
                    **kwargs,
                })
            except: raise error

            if name in PackageManager.vcs_packages:
                pkg2 = PackageManager.vcs_packages[name]
                if uri != pkg.link:
                    tree = pkg.get_dependency_tree()
                    tree2 = pkg2.get_dependency_tree()
                    raise RepositoryMissMatchError(
                        f"{pkg.name} is requested from 2 different places:\n"
                        f"{' --> '.join(tree2)}\n"
                        f"{' --> '.join(tree)}\n"
                    )
                PackageManager.vcs_ord.pop(PackageManager.vcs_ord.index(name))
                PackageManager.vcs_ord.append(name)

            elif pkg.normalized_name not in PackageManager.installed:
                PackageManager.vcs_packages[name] = pkg
                PackageManager.vcs_ord.append(name)
                self.packages_to_clone.append(pkg)

        elif uri not in PackageManager.pip_packages:
            PackageManager.pip_packages.append(uri)

    def install_vcs_packages(self):
        for name in reversed(PackageManager.vcs_ord):
            pkg = PackageManager.vcs_packages[name]

            # if pkg.link in PackageManager.satisfied:
            #     PackageManager.satisfied.append(pkg.link)
            #     log.info(f'{pkg.link} requirement already satisfied -> {name}=={PackageManager.installed[name]}')
            #     continue
            # else:

            # create wheel
            run('cd', pkg.path, '&&', executable, 'setup.py bdist_wheel --universal')
            dist = pkg.path + sep + 'dist'
            for fn in listdir(dist):
                if fn.endswith('.whl'):
                    wheel = dist + sep + fn
                    pip.install(wheel)
                    # print(get_metadata(wheel).requires_dist)
                    break


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        packages = self.configure_packages()

        with PackageManager.init(self.git, packages) as manager:
            if manager.vcs_packages:
                manager.clone_packages()

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

            if manager.vcs_packages:
                manager.install_vcs_packages()


class InstallTest(TestOperation, Install):
    def run(self): return Install.run(self)
