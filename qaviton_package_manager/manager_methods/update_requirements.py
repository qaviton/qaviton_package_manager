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


from qaviton_pip import pip
from qaviton_package_manager.manager_methods import ManagerOperation, TestOperation


class Update(ManagerOperation):
    def run(self):
        if len(self.packages) == 0 or self.packages[0] is None:
            self.get_packages_from_requirements()
        packages = self.configure_packages()
        if packages:
            pip.install(*packages, '--upgrade')


class UpdateTest(TestOperation, Update):
    def run(self): return Update.run(self)
