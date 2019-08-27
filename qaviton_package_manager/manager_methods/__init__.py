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
from abc import ABCMeta, abstractmethod
from urllib.parse import quote_plus as urlencode
from qaviton_package_manager.conf import supported_protocols
from qaviton_package_manager.utils.functions import get_requirements
from qaviton_package_manager.utils.git_wrapper import Git
from qaviton_package_manager.utils.logger import log
from qaviton_package_manager.utils.functions import get_package_name


def get_packages(requirements_path):
    with open(requirements_path) as f:
        packages = f.read().splitlines()
    return packages


class ManagerOperation(metaclass=ABCMeta):
    def __init__(self, git: Git, *packages):
        self.git = git
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
                        f'{urlencode(self.git.username)}:{urlencode(self.git.password)}@' + \
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


class Prep:
    def __init__(self, git: Git, package_name: str):
        self.root = os.getcwd()
        self.git = git

        self.setup_path = self.root+os.sep+'setup.py'
        self.package_name = get_package_name()

        self.pkg_path = self.root+os.sep+package_name
        self.pkg_init = self.pkg_path + os.sep + '__init__.py'

    def get_pkg_init(self):
        if not os.path.exists(self.pkg_path):
            log.warning(f"direcotory: {self.pkg_path} is missing")
            print("creating package...")
            os.mkdir(self.pkg_path)
            open(self.pkg_init, 'w').close()
            init = b''
        elif not os.path.exists(self.pkg_init):
            log.warning(f"file: {self.pkg_init} is missing")
            print("creating package init file...")
            open(self.pkg_init, 'w').close()
            init = b''
        else:
            with open(self.pkg_init, 'rb') as f:
                init = f.read()
        return init
