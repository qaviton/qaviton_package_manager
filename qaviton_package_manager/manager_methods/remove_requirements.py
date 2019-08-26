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


from qaviton_package_manager.manager_methods.clean_requirements import Clean


class Remove(Clean):
    def run(self):
        Clean.run(self)
        if self.packages:
            with open(self.requirements_path) as f:
                packages = f.readlines()
            for i, package in enumerate(packages):
                package = package.replace(' ', '').replace('\n', '')
                for removed in self.packages:
                    removed = removed.replace(' ', '')
                    # https://www.python.org/dev/peps/pep-0440/#version-specifiers
                    if removed == package\
                    or package.startswith(removed+'=')\
                    or package.startswith(removed + '>')\
                    or package.startswith(removed + '<')\
                    or package.startswith(removed + '~')\
                    or package.startswith(removed + '!'):
                        packages[i] = None
            packages = [pkg for pkg in packages if pkg is not None]
            with open(self.requirements_path, 'w') as f:
                f.writelines(packages)
