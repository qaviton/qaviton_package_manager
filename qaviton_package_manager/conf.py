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


LICENSE = 'LICENSE'
README = 'README.md'
REQUIREMENTS = 'requirements.txt'

# https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support
supported_protocols = (
    'git://',
    'git+http://',
    'git+https://',
    'git+ssh://',
    'git+git://',
    'git+file:///',
)

cred_protocols = (
    supported_protocols[2],
)

ignore_list = [
    'package.py',
    '.qaviton_package_manager_cache',
    '.qaviton_package_manager_cache.errors',
]
