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


import os
from qaviton_package_manager.utils.functions import get_requirements
from urllib.parse import quote_plus as urlencode
from abc import ABCMeta, abstractmethod
from qaviton_package_manager.conf import supported_protocols


def get_packages(requirements_path):
    with open(requirements_path) as f:
        packages = f.read().splitlines()
    return packages


class ManagerOperation(metaclass=ABCMeta):
    def __init__(self, username, password, *packages):
        self.username = username
        self.password = password
        self.packages = packages
        self.requirements_path = get_requirements(os.getcwd())
        self.run()

    def configure_packages(self):
        configured_packages = list(self.packages)
        for i, pkg in enumerate(configured_packages):
            for supported_protocol in supported_protocols:
                if pkg.startswith(supported_protocol):
                    configured_packages[i] = \
                        supported_protocol + \
                        f'{urlencode(self.username)}:{urlencode(self.password)}@' + \
                        pkg[len(supported_protocol):]
        return configured_packages

    def get_packages_from_requirements(self):
        self.packages = get_packages(self.requirements_path)

    @abstractmethod
    def run(self):
        pass


class Operation(metaclass=ABCMeta):
    def __init__(self, *packages):
        self.packages = packages
        self.requirements_path = get_requirements(os.getcwd())
        self.run()

    def configure_packages(self):
        return list(self.packages)

    def get_packages_from_requirements(self):
        self.packages = get_packages(self.requirements_path)

    @abstractmethod
    def run(self):
        pass
