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


from os import sep, listdir
from pkginfo import get_metadata
from tempfile import TemporaryDirectory
from qaviton_pip import pip
from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation
from qaviton_package_manager.utils.functions import package_match
from qaviton_package_manager.utils.logger import log
from qaviton_processes import run
from sys import executable


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        packages = ' '.join(self.configure_packages())

        vcs_packages = {}
        for pkg in packages:
            if 'git+' in pkg or '#egg=' in pkg:
                error = ValueError(
                    f"we detected an unsupported vcs installation:{pkg}\n"
                    "please view the supported vcs formats of pip here:\n"
                    "https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support\n\n"
                    "out of those, we dont support git://git.example.com/MyProject#egg=MyProject\n"
                    "our format is as follows:\n"
                    "git+protocol://git.example.com/MyProject.git@{branch}#egg=MyProject{:optional version tags}\n"
                    # ':1.1.1,1.1.2,!1.1.3,1.1.*,!1.1.*,!1.1,>1.1,<1.1,1.1-1.3,>=1.1,<=1.1,!(1.2-1.3)'
                    "we urge you to use https for a secure network transaction.")
                if 'git+' not in pkg or '#egg=' not in pkg: raise error
                try:
                    a = pkg.split('git+', 1)
                    b = a[1].rsplit('#egg=', 1)
                    c = b[0].split('.git@', 1)

                    if ':' in b[1]:
                        name, version = b[1].split(':', 1)
                        version = version.split(',')
                    else:
                        name, version = b[1], []

                    vcs_packages[name] = {
                        'link': pkg,
                        'url': c[0] + '.git',
                        'branch': c[1],
                        'vcs': 'git',
                        'protocol': a[1].split(':', 1)[0],
                        'version': version}
                except: raise error

        if vcs_packages:
            packages = [pkg for pkg in packages if 'git+' not in pkg]
            installed = pip('freeze').decode('utf-8').splitlines()
            with TemporaryDirectory() as tmp:
                for name, pkg in vcs_packages.items():
                    for i in installed:
                        if i.split('==')[0] == name.replace('_', '-'):
                            # lines = r.splitlines()
                            # version = None
                            # for line in lines:
                            #     v = b'Version: '
                            #     if line.startswith(v):
                            #         version = line[len(v):]
                            #         break
                            #
                            log.info(f'{name} from {pkg["link"]} requirement already satisfied')
                            break
                    else:
                        pkg['path'] = tmp+sep+name
                        repo = self.git.clone(
                            path=pkg['path'] ,
                            url=pkg['url'],
                            username=self.git.username,
                            password=self.git.password,
                            email=self.git.email)
                        pkg['versions'] = sorted(repo('tag --merged').decode('utf-8').splitlines())
                        if pkg["version"]:
                            # TODO: filter out the highest version
                            # version =
                            # repo(f'checkout tags/{version}')
                            version = pkg['versions'][-1]
                        else:
                            version = pkg['versions'][-1]
                        run('cd', pkg['path'], '&&', executable, 'setup.py bdist_wheel --universal')
                        dist = pkg['path'] + sep + 'dist'
                        for fn in listdir(dist):
                            if fn.endswith('.whl'):
                                wheel = dist + sep + fn
                                print(get_metadata(wheel).requires_dist)
                                break

        if packages:
            pip.install(packages)

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
