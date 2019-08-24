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


__author__ = 'Qaviton'
__version__ = '0.0.1'
__author_email__ = 'info@qaviton.com'
__description__ = 'a package manager for projects with private repositories'
__url__ = 'https://github.com/qaviton/qaviton_package_manager'
__license__ = 'Apache 2.0'


from pip.__main__ import _main


def install(package):
    _main(['install', package])


def uninstall(package):
    _main(['uninstall', package, '-y'])
