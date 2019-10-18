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
        self._LICENSE = None
        self._README = None
        self._REQUIREMENTS = None
        self._REQUIREMENTS_TESTS = None
        self._TESTS_DIR = None
        self._GIT_IGNORE = None
        self._PACKAGE = None
        self._COMPANY = None
        self._OWNER = None
        self._EMAIL = None
        self._LICENSE_TYPE = None

        if not exists(self._settings):
            self._set_default()
            self._save()
        else:
            self._load()

    def _set_default(self):
        if self._LICENSE is None: self._LICENSE = 'LICENSE'
        if self._README is None: self._README = 'README.md'
        if self._REQUIREMENTS is None: self._REQUIREMENTS = 'requirements.txt'
        if self._REQUIREMENTS_TESTS is None: self._REQUIREMENTS_TESTS = 'requirements-test.txt'
        if self._TESTS_DIR is None: self._TESTS_DIR = 'tests'
        if self._GIT_IGNORE is None: self._GIT_IGNORE = '.gitignore'
        if self._PACKAGE is None: self._PACKAGE = 'package.py'
        if self._COMPANY is None: self._COMPANY = ''
        if self._OWNER is None: self._OWNER = ''
        if self._EMAIL is None: self._EMAIL = ''
        if self._LICENSE_TYPE is None: self._LICENSE_TYPE = 'private'

    def _save(self):
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
                "LICENSE_TYPE": self._LICENSE_TYPE,
            }, f)

    def _load(self):
        with open(self._settings) as f:
            data = json.load(f)

        update = False
        while True:
            try:
                self._LICENSE = data["LICENSE"]
                self._README = data["README"]
                self._REQUIREMENTS = data["REQUIREMENTS"]
                self._REQUIREMENTS_TESTS = data["REQUIREMENTS_TESTS"]
                self._TESTS_DIR = data["TESTS_DIR"]
                self._GIT_IGNORE = data["GIT_IGNORE"]
                self._PACKAGE = data["PACKAGE"]
                self._COMPANY = data["COMPANY"]
                self._OWNER = data["OWNER"]
                self._EMAIL = data["EMAIL"]
                self._LICENSE_TYPE = data["LICENSE_TYPE"]
                break
            except AttributeError:
                self._set_default()
                update = True
        if update:
            self._save()

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

    @property
    def LICENSE_TYPE(self):
        return self._LICENSE_TYPE

    @LICENSE.setter
    def LICENSE(self, value):
        self._LICENSE = value
        self._save()

    @README.setter
    def README(self, value):
        self._README = value
        self._save()

    @REQUIREMENTS.setter
    def REQUIREMENTS(self, value):
        self._REQUIREMENTS = value
        self._save()

    @REQUIREMENTS_TESTS.setter
    def REQUIREMENTS_TESTS(self, value):
        self._REQUIREMENTS_TESTS = value
        self._save()

    @TESTS_DIR.setter
    def TESTS_DIR(self, value):
        self._TESTS_DIR = value
        self._save()

    @GIT_IGNORE.setter
    def GIT_IGNORE(self, value):
        self._GIT_IGNORE = value
        self._save()

    @PACKAGE.setter
    def PACKAGE(self, value):
        self._PACKAGE = value
        self._save()

    @COMPANY.setter
    def COMPANY(self, value):
        self._COMPANY = value
        self._save()

    @OWNER.setter
    def OWNER(self, value):
        self._OWNER = value
        self._save()

    @EMAIL.setter
    def EMAIL(self, value):
        self._EMAIL = value
        self._save()

    @LICENSE_TYPE.setter
    def LICENSE_TYPE(self, value):
        self._LICENSE_TYPE = value
        self._save()
