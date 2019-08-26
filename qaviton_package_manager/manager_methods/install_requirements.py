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


from qaviton_package_manager.utils.pip_wrapper import install as pip_install
from qaviton_package_manager.manager_methods import ManagerOperation


class Install(ManagerOperation):
    def run(self):
        install_requirements = len(self.packages) == 0 or self.packages[0] is None
        if install_requirements:
            self.get_packages_from_requirements()

        pip_install(*self.configure_packages())

        if not install_requirements and self.packages:
            with open(self.requirements_path) as f:
                packages = f.read().splitlines()
            for i, package in enumerate(packages):
                for added in self.packages:
                    if added == package:
                        packages[i] = None
            packages = [pkg for pkg in packages if pkg is not None]
            if packages:
                with open(self.requirements_path, 'a') as f:
                    f.write('\n'+'\n'.join(self.packages))
