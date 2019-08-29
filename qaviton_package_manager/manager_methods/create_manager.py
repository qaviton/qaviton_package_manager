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
from qaviton_package_manager.utils.git_wrapper import RepoData
from qaviton_package_manager.conf import LICENSE, README
from qaviton_package_manager.utils.functions import get_requirements
from qaviton_package_manager.utils.logger import log
from qaviton_package_manager.utils.functions import escape
from qaviton_package_manager.utils.git_wrapper import Git
from qaviton_package_manager.manager_methods import Prep


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
    def __init__(self, git: Git, package_name=None):
        log.info("creating git packaging system")

        if package_name is None:
            self.package_name = git.root.rsplit(os.sep, 1)[1]
            log.warning('package name not specified, selecting dir name:', self.package_name)
        else:
            self.package_name = package_name

        Prep.__init__(self, git, self.package_name)
        self.username = input("enter your git username:")
        self.pypi_user = input("enter your pypi username:")
        self.repo = RepoData()

        if os.path.exists(self.setup_path):
            raise FileExistsError("setup.py already exist")

        self.git_ignore = self.root + os.sep + '.gitignore'
        self.pkg = self.root + os.sep + 'package.py'
        self.run()

    def run(self):
        log.info("asserting package __init__.py file")
        init_content = self.get_pkg_init()

        log.info("asserting package LICENSE")
        license = self.get_license()

        log.info("asserting package README")
        readme = self.get_readme()

        log.info("asserting package requirements")
        requirements = get_requirements(self.root)

        self.handle_package_init(init_content, license)
        self.create_setup_file(readme, requirements)
        self.create_package_file()
        self.handle_git_ignore()

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
        return readme

    def handle_package_init(self, init_content: bytes, license: dict):
        missing_init_params = []

        tmp = b'\n' + init_content
        if b'\n__author__' not in tmp:
            log.warning(f'missing __author__ in init file, adding line: __author__ = {str(self.repo.username)[1:-1]}')
            missing_init_params.append(b'\n__author__ = "' + self.repo.username + b'"')

        if b'\n__version__' not in tmp:
            log.warning(f'missing __version__ in init file, adding line: __version__ = 0.0.1')
            missing_init_params.append(b'\n__version__ = "0.0.1"')

        if b'\n__author_email__' not in tmp:
            log.warning(f'missing __author_email__ in init file, adding line: __author_email__ = {str(self.repo.useremail)[1:-1]}')
            missing_init_params.append(b'\n__author_email__ = "' + self.repo.useremail + b'"')

        if b'\n__description__' not in tmp:
            description = self.package_name.replace('_', ' ')
            log.warning(f'missing __description__ in init file, adding line: __description__ = {description}')
            missing_init_params.append(b'\n__description__ = "' + bytes(description, 'utf-8') + b'"')

        if b'\n__url__' not in tmp:
            log.warning(f'missing __url__ in init file, adding line: __url__ = {str(self.repo.url)[1:-1]}')
            missing_init_params.append(b'\n__url__ = "' + self.repo.url + b'"')

        if b'\n__license__' not in tmp:
            if license["key"] is None:
                license["key"] = select_license()
            log.warning(f'missing __license__ in init file, adding line: __license__ = {license["key"]}')
            missing_init_params.append(b'\n__license__ = "' + bytes(license["key"], 'utf-8') + b'"')

        if missing_init_params:
            missing_init_params.append(b'\n')

        missing_init_params.append(init_content)
        content = b''.join(missing_init_params)
        with open(self.pkg_init, 'wb') as f:
            f.write(content)

    def create_setup_file(self, readme, requirements):
        content = b''.join([
            b'package_name = "' + bytes(self.package_name, 'utf-8') + b'"\n',
            b'\n',
            b'\n',
            b'if __name__ == "__main__":\n',
            b'    from sys import version_info as v\n',
            b'    from ' + bytes(self.package_name, 'utf-8') + b' import __author__, __version__, __author_email__, __description__, __url__, __license__\n',
            b'    from setuptools import setup, find_packages\n',
            b'    with open("' + bytes(requirements.rsplit(os.sep, 1)[1], 'utf-8') + b'") as f: requirements = f.read().splitlines()\n',
            b'    with open("' + bytes(readme.rsplit(os.sep, 1)[1], 'utf-8') + b'") as f: long_description = f.read()\n',
            b'    setup(\n',
            b'        name=package_name,\n',
            b'        version=__version__,\n',
            b'        author=__author__,\n',
            b'        author_email=__author_email__,\n',
            b'        description=__description__,\n',
            b'        long_description=long_description,\n',
            b'        long_description_content_type="text/markdown",\n',
            b'        url=__url__,\n',
            b'        packages=[pkg for pkg in find_packages() if pkg.startswith("' + bytes(self.package_name, 'utf-8') + b'")],\n',
            b'        license=__license__,\n',
            b'        classifiers=[\n',
            b'            f"Programming Language :: Python :: {v[0]}.{v[1]}",\n',
            b'        ],\n',
            b'        install_requires=requirements\n',
            b'    )\n',
        ])
        with open('setup.py', 'wb') as f:
            f.write(content)

    def create_package_file(self):
        if os.path.exists(self.pkg):
            raise FileExistsError("package.py already exist and may be used for other functionality")
        else:
            with open(self.pkg, 'w') as f:
                f.write(f'''from qaviton_package_manager import Manager

# this approach might not be safe enough
# Manager(
#     url="https://github.com/qaviton/qaviton_package_manager.git", 
#     username="contributor1", 
#     password="123456", 
#     pypi_user="owner", 
#     pypi_pass="654321"
# ).run(update=[], test=['python -m pytest tests'], build=[], upload=[])

# $> python package.py --password "pwd" --pypi_pass "p1"
Manager(
  url="{escape(str(self.git.get_url())[2:-1])}", 
  username="{escape(self.username)}",
  pypi_user="{escape(self.pypi_user)}",
).update().test('python -m pytest tests').build().upload().run()
'''                     )
        log.info('created package.py file')

    def handle_git_ignore(self):
        if not os.path.exists(self.git_ignore):
            log.warning("missing .gitignore file")
            print('creating .gitignore file')
            with open(self.git_ignore, 'w') as f:
                f.write('package.py\n')
        else:
            with open(self.git_ignore, 'a') as f:
                f.write('\npackage.py\n')
        log.info('added package.py to .gitignore file')
