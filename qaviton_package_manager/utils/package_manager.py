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
from stat import S_IWRITE
from shutil import rmtree
from os.path import exists
from sys import executable
from qaviton_pip import pip
from qaviton_git import Git
from typing import Dict, List
from qaviton_processes import run
# from pkginfo import get_metadata
from os import sep, listdir, chmod
from packaging.version import Version
from tempfile import TemporaryDirectory
from packaging.specifiers import SpecifierSet
from qaviton_package_manager.utils.logger import log
from qaviton_package_manager.exceptions import RepositoryMissMatchError, VersionFilterError
from qaviton_package_manager.utils.functions import normalize_package_name, get_package_name_from_requirement


class Package:
    def __init__(self, **kwargs):
        self._attr = {}
        self.link: str = None
        self.url: str = None
        self.branch: str = None
        self.vcs: str = None
        self.protocol: str = None
        self.version: str = None
        self.versions: [str] = []
        self.specifier: SpecifierSet = None
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
            self.path,
            self.url,
            PackageManager.git.username,
            PackageManager.git.password,
            PackageManager.git.email,
            f'--single-branch --branch "{self.branch}"')

    def set_version(self):
        self.versions = []
        bad_version_tags = []
        for v in sorted(self.repo('tag --merged').decode('utf-8').splitlines()):
            try:
                self.versions.append(Version(v))
            except:
                bad_version_tags.append(v)
        if bad_version_tags:
            log.warning(f"package {self.link} has invalid version tags:")
            for v in bad_version_tags:
                print(' ', v)
            log.info('you can fix this issue using: \n'
                     '  git push --delete origin tagName\n'
                     '  git tag -d tagName')
        # get version
        versions = sorted(self.specifier.filter(self.versions))
        if not versions:
            raise VersionFilterError(
                f"pkg {self.link} with specifiers {self.specifier} "
                f"has no valid version from its versions list: {self.versions}")
        self.version = versions[-1]
        self.repo(f'checkout tags/{self.version.__str__()}')

    def get_requirements(self):
        try:
            with open(self.requirements_path, encoding='utf-8') as f:
                requirements = f.read().splitlines()
            return requirements
        except FileNotFoundError as e:
            raise FileNotFoundError(f"{self.name} from {self.link} is missing requirements.txt file") from e


class PackageManager:
    installed: Dict[str, str]
    vcs_packages: Dict[str, Package]
    vcs_ord: List[str]
    pip_packages: List[str]
    uninstallable_packages: List[str]
    git: Git
    tmp: str
    _tmp: TemporaryDirectory

    @classmethod
    def init(cls, git: Git, packages: [str]):
        cls.installed = {}
        cls.vcs_packages: Dict[str, Package] = {}
        cls.vcs_ord = []
        cls.pip_packages = []
        cls.uninstallable_packages = []
        cls.git: Git = git
        for i in pip('freeze').decode('utf-8').splitlines():
            cls.installed.__setitem__(*i.split('=='))
        return cls(packages)

    def __enter__(self):
        PackageManager._tmp = TemporaryDirectory()
        PackageManager.tmp = PackageManager._tmp.name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # tmp = escape(PackageManager.tmp.replace("\\", "\\\\"))
        # python_code('import shutil', f'shutil.rmtree("{tmp}")')
        # PackageManager._tmp.cleanup()

        # def remove_readonly(func, path, exc):
        #     excvalue = exc[1]
        #     if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        #         os.chmod(path, stat.S_IWRITE | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        #         func(path)
        #     else:
        #         raise
        def remove_readonly(func, path, _):
            """Clear the readonly bit and reattempt the removal"""
            chmod(path, S_IWRITE)
            func(path)
        try:
            rmtree(PackageManager.tmp, onerror=remove_readonly)
        except:
            rmtree(PackageManager.tmp, onerror=remove_readonly)
        try:
            PackageManager._tmp.cleanup()
        except:
            pass

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

            # if pkg.normalized_name in PackageManager.installed:
            #     continue

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
                            # requirements[i] = f'{requirements_pkg.name}{"=="+requirements_pkg.version if requirements_pkg.version else ""}'
                            requirements[i] = ''
                requirements = [r for r in requirements if r != '']
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
                "we urge you to use https for a secure network transaction.")
            if 'git+' not in uri or '#egg=' not in uri: raise error
            try:
                a = uri.split('git+', 1)
                b = a[1].rsplit('#egg=', 1)
                c = b[0].split('.git@', 1)

                if ':' in b[1]:
                    name, specifier = b[1].split(':', 1)
                    uri = uri.rsplit(':')[0]
                else:
                    name, specifier = b[1], ''

                pkg = Package(**{
                    'link': uri,
                    'url': c[0] + '.git',
                    'branch': c[1],
                    'vcs': 'git',
                    'protocol': a[1].split(':', 1)[0],
                    'specifier': SpecifierSet(specifier),
                    'name': name,
                    'normalized_name': normalize_package_name(name),
                    'parent': self.parent,
                    **kwargs,
                })
            except: raise error

            if name in PackageManager.vcs_packages:
                pkg2 = PackageManager.vcs_packages[name]
                if pkg.link != pkg2.link:
                    tree = pkg.get_dependency_tree()
                    tree2 = pkg2.get_dependency_tree()
                    raise RepositoryMissMatchError(
                        f"{pkg.name} is requested from 2 different places:\n"
                        f"{' --> '.join(tree2)}\n"
                        f"{' --> '.join(tree)}\n"
                    )
                pkg2.specifier = pkg.specifier & pkg2.specifier
                PackageManager.vcs_ord.pop(PackageManager.vcs_ord.index(name))
                PackageManager.vcs_ord.append(name)

            else:
                if pkg.normalized_name not in PackageManager.installed:
                    PackageManager.uninstallable_packages.append(pkg.normalized_name)
                PackageManager.vcs_packages[name] = pkg
                PackageManager.vcs_ord.append(name)
            self.packages_to_clone.append(pkg)

        elif uri not in PackageManager.pip_packages:
            name, version = get_package_name_from_requirement(uri)
            name = normalize_package_name(name)
            if name not in PackageManager.installed:
                PackageManager.uninstallable_packages.append(name)
            PackageManager.pip_packages.append(uri)

    @staticmethod
    def create_wheels():
        wheels = []
        if not pip.exist('wheel'):
            pip.install('wheel')
        for name in reversed(PackageManager.vcs_ord):
            pkg = PackageManager.vcs_packages[name]

            # if pkg.link in PackageManager.satisfied:
            #     PackageManager.satisfied.append(pkg.link)
            #     log.info(f'{pkg.link} requirement already satisfied -> {name}=={PackageManager.installed[name]}')
            #     continue
            # else:

            # create wheel
            run('cd', pkg.path, '&&', executable, 'setup.py bdist_wheel --universal')
            for fn in listdir(pkg.dist_path):
                if fn.endswith('.whl'):
                    wheels.append(pkg.dist_path + sep + fn)
                    # print(get_metadata(wheel).requires_dist)
                    break
        return wheels

    @staticmethod
    def install_pip_packages():
        if PackageManager.pip_packages:
            pip.install(*PackageManager.pip_packages)

    def install_vcs_packages(self):
        wheels = self.create_wheels()
        if wheels:
            pip.install(*wheels)

    @staticmethod
    def update_pip_packages():
        if PackageManager.pip_packages:
            pip.upgrade(*PackageManager.pip_packages)

    def update_vcs_packages(self):
        wheels = self.create_wheels()
        if wheels:
            pip.upgrade(*wheels)

    @staticmethod
    def uninstall_packages():
        if PackageManager.uninstallable_packages:
            pip.uninstall(*PackageManager.uninstallable_packages)
