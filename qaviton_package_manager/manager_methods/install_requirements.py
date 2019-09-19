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

from os import sep
from tempfile import TemporaryDirectory
from qaviton_pip import pip
from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation
from qaviton_package_manager.utils.functions import package_match
from qaviton_package_manager.utils.logger import log


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        packages = ' '.join(self.configure_packages())

        # vcs_packages = {pkg.rsplit('#egg=', 1)[1]: {'link':pkg} for i, pkg in enumerate(packages) if 'git+' in pkg and '#egg=' in pkg}
        # for i, pkg in enumerate(packages):
        #     if 'git+' in pkg or '#egg=' in pkg:
        #         if 'git+' not in pkg or '#egg=' not in pkg:
        #             raise ValueError(
        #                 "we detected an unsupported vcs installation\n"
        #                 "please view the supported vcs formats of pip here:\n"
        #                 "https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support\n\n"
        #                 "out of those, we dont support git://git.example.com/MyProject#egg=MyProject\n"
        #                 "our format is as follows: git+protocol://git.example.com/MyProject.git@#egg=MyProject\n")
        #
        # if vcs_packages:
        #     packages = [pkg for pkg in packages if 'git+' not in pkg]
        #     with TemporaryDirectory() as tmp:
        #         for name, pkg in vcs_packages.items():
        #             if pip.exist(name):
        #                 log.info(f'{name} from {pkg["link"]} requirement already satisfied')
        #             else:
        #                 try:
        #                     pkg['url'] = pkg['link'].split('git+', 1)[1].rsplit('#egg=', 1)[0]
        #                     .rsplit('@', 1)[0]
        #                 except Exception as e:
        #                     log.error("bad ")
        #                 self.git.clone(
        #                     path=tmp+sep+name,
        #                     url=url.replace('git+', '', 1),
        #                     username=self.git.username,
        #                     password=self.git.password,
        #                     email=self.git.email)

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
