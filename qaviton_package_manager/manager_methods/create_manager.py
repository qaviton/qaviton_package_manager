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
from qaviton_pip import pip
from qaviton_processes import escape
from qaviton_package_manager.conf import LICENSE, README, PACKAGE, GIT_IGNORE
from qaviton_package_manager.utils.functions import get_requirements, get_test_requirements
from qaviton_package_manager.conf import REQUIREMENTS, REQUIREMENTS_TESTS, TESTS_DIR
from qaviton_package_manager.utils.logger import log
from qaviton_git import Git
from qaviton_package_manager.manager_methods import Prep
from qaviton_package_manager.conf import ignore_list
from qaviton_package_manager.utils.cryp import encrypt


class HTTP:
    _session = None
    @staticmethod
    def get():
        if HTTP._session is None:
            import requests
            HTTP._session = requests.Session()
        return HTTP._session


def select_license():
    log.info('fetching licenses')
    http = HTTP.get()
    r = http.get('https://api.github.com/licenses')
    r.raise_for_status()
    licenses: list = r.json()
    while True:
        print("\nSelect a License:")
        for i, l in enumerate(licenses):
            print(f"  ({i + 1}) {l['key']}")
        try:
            return licenses[int(input("")) - 1]['key']
        except:
            print('invalid input, please select a valid number')


class Create(Prep):
    def __init__(self, git: Git, pypi_user, pypi_pass, package_name=None):
        log.info("creating git packaging system")

        if package_name is None:
            self.package_name = git.root.rsplit(os.sep, 1)[1]
            log.warning('package name not specified, selecting dir name:', self.package_name)
        else:
            self.package_name = package_name

        Prep.__init__(self, git, self.package_name)

        if os.path.exists(self.setup_path):
            raise FileExistsError("setup.py already exist")

        self.pypi_user = pypi_user
        self.pypi_pass = pypi_pass
        self.git_ignore = self.root + os.sep + GIT_IGNORE
        self.pkg = self.root + os.sep + PACKAGE
        self.run()

    def run(self):
        log.info("asserting package __init__.py file")
        init_content = self.get_pkg_init()

        log.info("asserting package LICENSE")
        license = self.get_license()

        log.info("asserting package README")
        readme = self.get_readme()

        log.info("asserting package requirements")
        requirements = self.set_requirements()

        log.info("asserting package testing requirements")
        self.set_test_requirements()

        package_params = self.handle_package_init(init_content, license)
        self.create_setup_file(readme, requirements, package_params)
        self.create_package_file()
        self.handle_git_ignore()

    def set_requirements(self):
        path = get_requirements(self.root)
        if not os.path.exists(path):
            print(f'{REQUIREMENTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS = "filename"')
            name = input(f'select REQUIREMENTS filename({REQUIREMENTS} default):')
            if not name: name = REQUIREMENTS
            path = self.root + os.sep + name
            if not os.path.exists(path):
                pip.freeze(path)
                self.git.add(path)
        return path

    def set_test_requirements(self):
        path = get_test_requirements(self.root)
        if not os.path.exists(path):
            print(f'{REQUIREMENTS_TESTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS_TESTS = "filename"')
            name = input(f'select REQUIREMENTS_TESTS filename({REQUIREMENTS_TESTS} default):')
            if not name: name = REQUIREMENTS_TESTS
            path = self.root + os.sep + name
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write('pytest')
                self.git.add(path)
        path = self.root + os.sep + TESTS_DIR
        if not os.path.exists(path):
            print(f'{TESTS_DIR} not found\nP.S. you can change the default tests directory with qaviton_package_manager.conf.TESTS_DIR = "filename"')
            name = input(f'select TESTS_DIR filename({TESTS_DIR} default):')
            if not name: name = TESTS_DIR
            path = self.root + os.sep + name
            if not os.path.exists(path):
                os.mkdir(path)
                init_path = path + os.sep + '__init__.py'
                open(init_path, 'w').close()
                self.git.add(init_path)

    def get_license(self):
        license = self.root + os.sep + LICENSE
        key = None
        if not os.path.exists(license):
            log.warning(f'{LICENSE} not found\nP.S. you can change the default license filename with qaviton_package_manager.conf.LICENSE = "filename"')
            name = input(f'select LICENSE filename({LICENSE} default):')
            if not name: name = LICENSE
            license = self.root + os.sep + name
            if not os.path.exists(license):
                key = select_license()
                print(f'creating file: {license}')
                http = HTTP.get()
                r = http.get(f'https://api.github.com/licenses/{key}')
                r.raise_for_status()
                content = r.json()['body']
                with open(license, 'w') as f:
                    f.write(content)
                self.git.add(license)
        return {'file': license, 'key': key}

    def get_readme(self):
        readme = self.root + os.sep + README
        if not os.path.exists(readme):
            log.warning(f'{README} not found\nP.S. you can change the default readme filename with qaviton_package_manager.conf.README = "filename"')
            name = input(f'select README filename({README} default):')
            if not name: name = README
            readme = self.root + os.sep + name
            if not os.path.exists(readme):
                print(f'creating file: {readme}')
                with open(readme, 'w') as f:
                    f.write(self.package_name.replace('_', ' '))
                self.git.add(readme)
        return readme

    def handle_package_init(self, init_content: bytes, license: dict):
        package_params = {}

        tmp = b'\n' + init_content
        if b'\n__author__' not in tmp:
            log.warning(f'missing __author__ in init file')
            package_params['author'] = b'"' + escape(self.git.username).encode('utf-8') + b'"'
        else:
            package_params['author'] = tmp.split(b'\n__author__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()

        if b'\n__version__' not in tmp:
            log.warning(f'missing __version__ in init file')
            package_params['version'] = b'"0.0.1"'
        else:
            package_params['version'] = tmp.split(b'\n__version__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()

        if b'\n__author_email__' not in tmp:
            log.warning(f'missing __author_email__ in init file')
            package_params['email'] = b'"' + escape(self.git.email).encode('utf-8') + b'"'
        else:
            package_params['email'] = tmp.split(b'\n__author_email__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()

        if b'\n__description__' not in tmp:
            description = self.package_name.replace('_', ' ')
            log.warning(f'missing __description__ in init file')
            package_params['description'] = b'"' + description.encode('utf-8') + b'"'
        else:
            package_params['description'] = tmp.split(b'\n__description__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()

        if b'\n__url__' not in tmp:
            log.warning(f'missing __url__ in init file')
            package_params['url'] = b'"' + escape(self.git.url.replace('.git', '')).encode('utf-8') + b'"'
        else:
            package_params['url'] = tmp.split(b'\n__url__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()

        if b'\n__license__' not in tmp:
            if license["key"] is None:
                license["key"] = select_license()
            log.warning(f'missing __license__ in init file')
            package_params['license'] = b'"' + license["key"].encode('utf-8') + b'"'
        else:
            package_params['license'] = tmp.split(b'\n__license__', 1)[1].split(b'=', 1)[1].split(b'\n', 1)[0].strip()
        return package_params

    def create_setup_file(self, readme, requirements, package_params):
        path = self.root + os.sep + 'setup.py'
        if not os.path.exists(path):
            content = b''.join([
                b'package_name = "' + bytes(self.package_name, 'utf-8') + b'"\n',
                b'\n',
                b'\n',
                b'if __name__ == "__main__":\n',
                b'    from sys import version_info as v\n',
                b'    from setuptools import setup, find_packages\n',
                b'    with open("' + bytes(requirements.rsplit(os.sep, 1)[1], 'utf-8') + b'") as f: requirements = f.read().splitlines()\n',
                b'    with open("' + bytes(readme.rsplit(os.sep, 1)[1], 'utf-8') + b'", encoding="utf8") as f: long_description = f.read()\n',
                b'    setup(\n',
                b'        name=package_name,\n',
                b'        version=' + package_params['version'] + b',\n',
                b'        author=' + package_params['author'] + b',\n',
                b'        author_email=' + package_params['email'] + b',\n',
                b'        description=' + package_params['description'] + b',\n',
                b'        long_description=long_description,\n',
                b'        long_description_content_type="text/markdown",\n',
                b'        url=' + package_params['url'] + b',\n',
                b'        packages=[pkg for pkg in find_packages() if pkg.startswith(package_name)],\n',
                b'        license=' + package_params['license'] + b',\n',
                b'        classifiers=[\n',
                b'            f"Programming Language :: Python :: {v[0]}.{v[1]}",\n',
                b'        ],\n',
                b'        install_requires=requirements\n',
                b'    )\n',
            ])
            with open(path, 'wb') as f:
                f.write(content)
            self.git.add(path)

    def create_package_file(self):
        if os.path.exists(self.pkg):
            raise FileExistsError("package.py already exist and may be used for other functionality")
        else:
            key, token = encrypt(
                url=self.git.url,
                email=self.git.email,
                username=self.git.username,
                password=self.git.password,
                pypi_user=self.pypi_user,
                pypi_pass=self.pypi_pass,
            )
            upload = "\n        lambda: manager.upload()," if self.pypi_user and self.pypi_pass else ""
            with open(self.pkg, 'w') as f:
                f.write(f'''from qaviton_package_manager import Manager, decypt


manager = Manager(**decypt(
    key={key},
    token={token},
))


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        lambda: manager.build(),{upload}
    )
'''                     )
        log.info('created package.py file')

    def handle_git_ignore(self):
        if not os.path.exists(self.git_ignore):
            log.warning("missing .gitignore file")
            print('creating .gitignore file')
            with open(self.git_ignore, 'w') as f:
                f.write('\n'.join(ignore_list))
            self.git.add(self.git_ignore)
        else:
            with open(self.git_ignore) as f:
                lines = f.read().splitlines()
            with open(self.git_ignore, 'a') as f:
                f.write('\n'+'\n'.join([line for line in ignore_list if line not in lines]))
        log.info('added content to .gitignore file')
