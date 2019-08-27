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
from qaviton_package_manager.utils.git_wrapper import Git
from qaviton_package_manager.manager_methods.create_manager import Create
from qaviton_package_manager.manager_methods.install_requirements import Install
from qaviton_package_manager.manager_methods.update_requirements import Update
from qaviton_package_manager.manager_methods.remove_requirements import Remove
from qaviton_package_manager.manager_methods.clean_requirements import Clean
from qaviton_package_manager.manager_methods.save_version import Build


class Manager:
    def __init__(self, url=None, username=None, password=None, **kwargs):
        self.url = url
        self.username = username
        self.password = password
        self.kwargs = {}
        self._set_kwargs(kwargs)
        self._ord = list(kwargs.keys())
        self._get_external_args()
        self.git = Git(self.url, self.username, self.password)
        del self.username
        del self.password

    def _set_kwargs(self, kwargs):
        self.kwargs.update({key: (value if isinstance(value, list) else [value]) for key, value in kwargs.items()})

    def _get_external_args(self):
        length = len(argv)
        i = 4
        if length > i:
            self.url = argv[1]
            self.username = argv[2]
            self.password = argv[3]
            while i < length:
                arg: str = argv[i]
                if arg.startswith('--'):
                    api = arg[2:]
                    args = []
                    if not i+1 >= len(argv) and not argv[i+1].startswith('--'):
                        while not argv[i+1].startswith('--'):
                            i += 1
                            args.append(argv[i])
                    self.kwargs[api] = args
                    if api not in self._ord:
                        self._ord.append(api)
                i += 1

    def run(self, **kwargs):
        self._set_kwargs(kwargs)
        self._ord.extend(kwargs.keys())
        for key in self._ord:
            getattr(self, key)(*self.kwargs[key])

    def create(self, package_name=None): Create(package_name)
    def install(self, *packages): Install(self.git, *packages)
    def update(self, *packages): Update(self.git, *packages)
    def clean(self, *packages): Clean(*packages)
    def remove(self, *packages): Remove(*packages)
    def build(self, package_name, to_branch='build', version=None): Build(self.git, package_name, to_branch=to_branch, version=version)
