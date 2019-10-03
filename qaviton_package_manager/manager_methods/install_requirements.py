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

from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation
from qaviton_package_manager.utils.functions import package_match
from qaviton_package_manager.utils.package_manager import PackageManager


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        packages = self.configure_packages()

        with PackageManager.init(self.git, packages) as manager:
            try:
                if manager.vcs_packages:
                    manager.clone_packages()

                if packages:
                    manager.install_pip_packages()

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
                        with open(self.requirements_path, encoding='utf-8') as f:
                            requirements = f.read().splitlines()
                        for i, requirement in enumerate(requirements):
                            for package in self.packages:
                                if package_match(package, requirement):
                                    requirements[i] = None
                        requirements = [pkg+'\n' for pkg in requirements if pkg is not None]
                        for pkg in list({pkg+'\n' for pkg in self.packages}): requirements.append(pkg)
                        with open(self.requirements_path, 'w') as f:
                            f.writelines(requirements)

                if manager.vcs_packages:
                    manager.install_vcs_packages()
                    
            except Exception as e:
                manager.uninstall_packages()
                raise e


class InstallTest(TestOperation, Install):
    def run(self): return Install.run(self)
