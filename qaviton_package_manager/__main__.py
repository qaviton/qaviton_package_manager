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


def main():
    from os.path import exists
    if exists('package'):
        manager = __import__('package', globals(), locals(), ['manager'], 0)
        manager.run()
        return manager
    else:
        from qaviton_package_manager.manager import Manager
        return Manager().run()


if __name__ == '__main__':
    main()
