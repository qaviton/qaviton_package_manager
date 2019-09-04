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
from qaviton_package_manager.utils.functions import upload_to_pypi, get_package_name


class Upload:
    def __init__(self, pypi_user, pypi_pass):
        if not pip.exist('wheel'):
            pip.install('wheel')
        if not pip.exist('twine'):
            pip.install('twine')
        upload_to_pypi(pypi_user, pypi_pass)
        print('package uploaded to pypi')
        print('you can now install this package:')
        print(f'pip install {get_package_name()}')
