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
    from os import getcwd, sep
    root = getcwd()
    pkg = root+sep+'package.py'
    if exists(pkg):
        from qaviton_helpers import import_path
        try:
            manager = import_path(pkg).manager
        except Exception as e:
            from qaviton_package_manager.utils.logger import log
            log.warning(e)
            log.info(f"could not retrieve 'manager' parameter from {pkg}")
            log.info("creating a new manager")
        else:
            return manager.run()
    from qaviton_package_manager.manager import Manager
    return Manager().run()


if __name__ == '__main__':
    main()
