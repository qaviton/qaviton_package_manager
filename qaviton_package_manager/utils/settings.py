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
    default = {
        "LICENSE": 'LICENSE',
        "README": 'README.md',
        "REQUIREMENTS": 'requirements.txt',
        "REQUIREMENTS_TESTS": 'requirements-test.txt',
        "TESTS_DIR": 'tests',
        "GIT_IGNORE": '.gitignore',
        "PACKAGE": 'package.py',
        "COMPANY": '',
        "OWNER": '',
        "EMAIL": '',
        "LICENSE_TYPE": 'private',
    }
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
            for setting in self.default:
                setattr(self, '_' + setting, self.default[setting])
            self._save()
        else:
            self._load()

    def _save(self):
        with open(self._settings, 'w') as f:
            json.dump({setting: getattr(self, '_'+setting) for setting in self.default}, f)

    def _load(self):
        with open(self._settings) as f:
            data = json.load(f)

        update = False
        for setting in self.default:
            if setting not in data:
                update = True
                data[setting] = self.default[setting]
            setattr(self, '_'+setting, data[setting])

        if update:
            self._save()

    @property
    def LICENSE(self): return self._LICENSE
    @property
    def README(self): return self._README
    @property
    def REQUIREMENTS(self): return self._REQUIREMENTS
    @property
    def REQUIREMENTS_TESTS(self): return self._REQUIREMENTS_TESTS
    @property
    def TESTS_DIR(self): return self._TESTS_DIR
    @property
    def GIT_IGNORE(self): return self._GIT_IGNORE
    @property
    def PACKAGE(self): return self._PACKAGE
    @property
    def COMPANY(self): return self._COMPANY
    @property
    def OWNER(self): return self._OWNER
    @property
    def EMAIL(self): return self._EMAIL
    @property
    def LICENSE_TYPE(self): return self._LICENSE_TYPE

    @LICENSE.setter
    def LICENSE(self, value): self._LICENSE = value; self._save()
    @README.setter
    def README(self, value): self._README = value; self._save()
    @REQUIREMENTS.setter
    def REQUIREMENTS(self, value): self._REQUIREMENTS = value; self._save()
    @REQUIREMENTS_TESTS.setter
    def REQUIREMENTS_TESTS(self, value): self._REQUIREMENTS_TESTS = value; self._save()
    @TESTS_DIR.setter
    def TESTS_DIR(self, value): self._TESTS_DIR = value; self._save()
    @GIT_IGNORE.setter
    def GIT_IGNORE(self, value): self._GIT_IGNORE = value; self._save()
    @PACKAGE.setter
    def PACKAGE(self, value): self._PACKAGE = value; self._save()
    @COMPANY.setter
    def COMPANY(self, value): self._COMPANY = value; self._save()
    @OWNER.setter
    def OWNER(self, value): self._OWNER = value; self._save()
    @EMAIL.setter
    def EMAIL(self, value): self._EMAIL = value; self._save()
    @LICENSE_TYPE.setter
    def LICENSE_TYPE(self, value): self._LICENSE_TYPE = value; self._save()
