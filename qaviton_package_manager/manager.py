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
from traceback import format_exc
from qaviton_git import Git
from qaviton_package_manager.manager_methods.create_manager import Create
from qaviton_package_manager.manager_methods.install_requirements import Install, InstallTest
from qaviton_package_manager.manager_methods.update_requirements import Update, UpdateTest
from qaviton_package_manager.manager_methods.remove_requirements import Remove, RemoveTest
from qaviton_package_manager.manager_methods.clean_requirements import Clean, CleanTest
from qaviton_package_manager.manager_methods.distribute_to_git import Build
from qaviton_package_manager.manager_methods.distribute_to_pypi import Upload
from qaviton_package_manager.manager_methods.test_package import Test
from qaviton_package_manager.utils.cache_cred import Cache
from qaviton_package_manager.exceptions import BuildAbortError


class Manager:
    def __init__(
        self,
        url=None,
        username=None,
        password=None,
        email=None,
        pypi_user=None,
        pypi_pass=None,
        docker_url=None,
        docker_user=None,
        docker_pass=None,
        docker_email=None,
        cache_timeout=None,
        **kwargs,
    ):
        self.vars = {
            'url': url,
            'username': username,
            'password': password,
            'email': email,
            'pypi_user': pypi_user,
            'pypi_pass': pypi_pass,
            'docker_url': docker_url,
            'docker_user': docker_user,
            'docker_pass': docker_pass,
            'docker_email': docker_email,
            'cache_timeout': cache_timeout,
        }
        self.kwargs = {}
        self._set_kwargs(kwargs)
        self._ord = list(kwargs.keys())
        self._get_external_args()
        self.git = Git(
            url=self.vars['url'],
            username=self.vars['username'],
            password=self.vars['password'],
            email=self.vars['email'],
        )
        self.cache = Cache()
        if self.vars['cache_timeout']:
            self.vars['cache_timeout'] = int(self.vars['cache_timeout'])
            if not self.cache.server_is_alive():
                self.cache.create_server(**self.vars)
            self.vars_sync()
        self.test = Test()

    def vars_sync(self):
        self.vars['url'] = self.git.url
        self.vars['username'] = self.git.username
        self.vars['password'] = self.git.password
        self.vars['email'] = self.git.email
        for key, value in self.vars.items():
            if not value:
                response = self.cache.get(key)
                if key in response:
                    self.vars[key] = response[key]
            else:
                self.cache.post(**{key: value})

    def _set_kwargs(self, kwargs):
        for key, value in kwargs.items():
            if key in self.vars:
                self.vars[key] = value
            else:
                self.kwargs[key] = value if isinstance(value, list) else [value]

    def _get_external_args(self):
        length = len(argv)
        i = 1
        if length > i:
            while i < length:
                arg: str = argv[i]
                if arg.startswith('--'):
                    api = arg[2:]
                    if api in self.vars:
                        try:
                            self.vars[api] = argv[i+1]
                        except:
                            raise ValueError(f"parameter {api} is missing a value")
                        i += 2
                        continue
                    args = []
                    while not i+1 >= len(argv) and not argv[i+1].startswith('--'):
                        i += 1
                        args.append(argv[i])
                    self.kwargs[api] = args
                    if api not in self._ord:
                        self._ord.append(api)
                i += 1

    def _run(self, f, *args, **kwargs):
        try:
            return f(*args, **kwargs)
        except SyntaxError as e:
            raise e
        except BuildAbortError as e:
            print(e)
            exit(0)
        except:
            print(format_exc())
            exit(code=1)

    def run(self, *functions, **kwargs):
        self._set_kwargs(kwargs)
        self._ord.extend(kwargs.keys())
        if not self._ord:
            for f in functions: self._run(f)
        else:
            for key in self._ord:
                if hasattr(self, key):
                    self._run(getattr(self, key), *self.kwargs[key])

    def create(self, package_name=None): Create(self.git, self.vars['pypi_user'], self.vars['pypi_pass'], package_name); return self
    def install(self, *packages): Install(self.git, *packages); return self
    def install_test(self, *packages): InstallTest(self.git, *packages); return self
    def update(self, *packages): Update(self.git, *packages); return self
    def update_test(self, *packages): UpdateTest(self.git, *packages); return self
    def clean(self, *packages): Clean(self.git, *packages); return self
    def clean_test(self, *packages): CleanTest(self.git, *packages); return self
    def uninstall(self, *packages): Remove(self.git, *packages); return self
    def uninstall_test(self, *packages): RemoveTest(self.git, *packages); return self
    def build(self, to_branch='build/latest', version=None): Build(self.git, to_branch=to_branch, version=version); return self
    def upload(self): Upload(self.vars['pypi_user'], self.vars['pypi_pass']); return self
    def should_build(self, from_branch=None, to_branch='build/latest'):
        current_branch = self.git.get_current_branch()
        if from_branch is None: from_branch = current_branch
        if from_branch != current_branch:
            self.git.switch(from_branch)
            if self.git.has_remote():
                self.git.pull()
        if self.git.has_commitable_changes() or self.git.can_merge(into=to_branch): return self
        raise BuildAbortError('no detectable changes, build aborted')
