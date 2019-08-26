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


from sys import argv
from qaviton_package_manager.manager_methods.create_manager import Create
from qaviton_package_manager.manager_methods.install_requirements import Install
from qaviton_package_manager.manager_methods.update_requirements import Update
from qaviton_package_manager.manager_methods.remove_requirements import Remove
from qaviton_package_manager.manager_methods.clean_requirements import Clean
from qaviton_package_manager.manager_methods.save_version import Build


class Manager:
    def __init__(self, username=None, password=None, **kwargs):
        self.username = username
        self.password = password
        self._ord = []
        self.kwargs = kwargs
        self._get_external_args()

    def _get_external_args(self):
        length = len(argv)
        i = 1
        if self.username is None:
            try:
                self.username = argv[i]
            except:
                raise ValueError("missing username")
            i += 1
        if self.password is None:
            try:
                self.password = argv[i]
            except:
                raise ValueError("missing password")
            i += 1
        if length > i:
            while i < length:
                arg: str = argv[i]
                if arg.startswith('--'):
                    key = arg[2:]
                    if i+1 >= len(argv):
                        value = None
                    elif argv[i+1].startswith('--'):
                        value = None
                    else:
                        value = []
                        while not argv[i+1].startswith('--'):
                            i += 1
                            value.append(argv[i])
                        if len(value) == 1:
                            value = value[0]
                    self.kwargs[key] = value
                    self._ord.append(key)
                i += 1

    def run(self, **kwargs):
        self.kwargs.update(kwargs)
        self._ord.extend(kwargs.keys())
        for key in self._ord:
            getattr(self, key)(self.kwargs[key])

    def create(self, package_name=None):         Create(package_name)
    def install(self, *packages):                Install(self.username, self.password, *packages)
    def update(self, *packages):                 Update(self.username, self.password, *packages)
    def clean(self, *packages):                  Clean(*packages)
    def remove(self, *packages):                 Remove(*packages)
    def build(self, package_name, version=None): Build(package_name, version)
