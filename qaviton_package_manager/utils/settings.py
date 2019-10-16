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
from os.path import dirname, exists
from os import sep
import json


class Settings:
    def __init__(self):
        self._settings = dirname(__file__) + sep + 'settings.json'
        if not exists(self._settings):
            self._LICENSE = 'LICENSE'
            self._README = 'README.md'
            self._REQUIREMENTS = 'requirements.txt'
            self._REQUIREMENTS_TESTS = 'requirements-test.txt'
            self._TESTS_DIR = 'tests'
            self._GIT_IGNORE = '.gitignore'
            self._PACKAGE = 'package.py'
            self._COMPANY = ''
            self._OWNER = ''
            self._EMAIL = ''
            self.save()
        else:
            self.load()

    def save(self):
        with open(self._settings, 'w') as f:
            json.dump({
                "LICENSE": self._LICENSE,
                "README": self._README,
                "REQUIREMENTS": self._REQUIREMENTS,
                "REQUIREMENTS_TESTS": self._REQUIREMENTS_TESTS,
                "TESTS_DIR": self._TESTS_DIR,
                "GIT_IGNORE": self._GIT_IGNORE,
                "PACKAGE": self._PACKAGE,
                "COMPANY": self._COMPANY,
                "OWNER": self._OWNER,
                "EMAIL": self._EMAIL,
            }, f)

    def load(self):
        with open(self._settings) as f:
            data = json.load(f)
        self._LICENSE = data["LICENSE"]
        self._README = data["README"]
        self._REQUIREMENTS = data["REQUIREMENTS"]
        self._REQUIREMENTS_TESTS = data["REQUIREMENTS_TESTS"]
        self._TESTS_DIR = data["TESTS_DIR"]
        self._GIT_IGNORE = data["GIT_IGNORE"]
        self._PACKAGE = data["PACKAGE"]

    @property
    def LICENSE(self):
        return self._LICENSE

    @property
    def README(self):
        return self._README

    @property
    def REQUIREMENTS(self):
        return self._REQUIREMENTS

    @property
    def REQUIREMENTS_TESTS(self):
        return self._REQUIREMENTS_TESTS

    @property
    def TESTS_DIR(self):
        return self._TESTS_DIR

    @property
    def GIT_IGNORE(self):
        return self._GIT_IGNORE

    @property
    def PACKAGE(self):
        return self._PACKAGE

    @property
    def COMPANY(self):
        return self._COMPANY

    @property
    def OWNER(self):
        return self._OWNER

    @property
    def EMAIL(self):
        return self._EMAIL

    @LICENSE.setter
    def LICENSE(self, value):
        self._LICENSE = value
        self.save()

    @README.setter
    def README(self, value):
        self._README = value
        self.save()

    @REQUIREMENTS.setter
    def REQUIREMENTS(self, value):
        self._REQUIREMENTS = value
        self.save()

    @REQUIREMENTS_TESTS.setter
    def REQUIREMENTS_TESTS(self, value):
        self._REQUIREMENTS_TESTS = value
        self.save()

    @TESTS_DIR.setter
    def TESTS_DIR(self, value):
        self._TESTS_DIR = value
        self.save()

    @GIT_IGNORE.setter
    def GIT_IGNORE(self, value):
        self._GIT_IGNORE = value
        self.save()

    @PACKAGE.setter
    def PACKAGE(self, value):
        self._PACKAGE = value
        self.save()

    @COMPANY.setter
    def COMPANY(self, value):
        self._COMPANY = value
        self.save()

    @OWNER.setter
    def OWNER(self, value):
        self._OWNER = value
        self.save()

    @EMAIL.setter
    def EMAIL(self, value):
        self._EMAIL = value
        self.save()
