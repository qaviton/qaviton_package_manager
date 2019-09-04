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

from qaviton_package_manager.manager_methods import TestOperation
from qaviton_package_manager.manager_methods.clean_requirements import Clean
from qaviton_package_manager.utils.functions import package_match


class Remove(Clean):
    def run(self):
        if Clean.run(self):
            if self.packages:
                with open(self.requirements_path) as f:
                    requirements = f.readlines()
                for i, line in enumerate(requirements):
                    requirement = line.replace(' ', '').replace('\n', '')
                    for removed in self.packages:
                        if package_match(removed.replace(' ', ''), requirement):
                            requirements[i] = None
                with open(self.requirements_path, 'w') as f:
                    f.writelines([pkg for pkg in requirements if pkg is not None])


class RemoveTest(TestOperation, Remove):
    def run(self): return Clean.run(self)
