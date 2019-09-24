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


LICENSE = 'LICENSE'
README = 'README.md'
REQUIREMENTS = 'requirements.txt'
REQUIREMENTS_TESTS = 'requirements-test.txt'
TESTS_DIR = 'tests'
GIT_IGNORE = '.gitignore'
PACKAGE = 'package.py'


# https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support
supported_protocols = (
    'git://',
    'git+http://',
    'git+https://',
    'git+ssh://',
    'git+git://',
    'git+file:///',
)

cred_protocols = (
    supported_protocols[2],
)

version_specifiers = '=!~<>'
invalid_package_chars = ', ' + version_specifiers

ignore_list = [
    '# Byte-compiled / optimized / DLL files',
    '__pycache__/',
    '*.py[cod]',
    '*$py.class',
    '',
    '# C extensions',
    '*.so',
    '',
    '# Distribution / packaging',
    '.Python',
    'build/',
    'develop-eggs/',
    'dist/',
    'downloads/',
    'eggs/',
    '.eggs/',
    'lib/',
    'lib64/',
    'parts/',
    'sdist/',
    'var/',
    'wheels/',
    '*.egg-info/',
    '.installed.cfg',
    '*.egg',
    'MANIFEST',
    '',
    '# PyInstaller',
    '#  Usually these files are written by a python script from a template',
    '#  before PyInstaller builds the exe, so as to inject date/other infos into it.',
    '*.manifest',
    '*.spec',
    '',
    '# Installer logs',
    'pip-log.txt',
    'pip-delete-this-directory.txt',
    '',
    '# Unit test / coverage reports',
    'htmlcov/',
    '.tox/',
    '.coverage',
    '.coverage.*',
    '.cache',
    'nosetests.xml',
    'coverage.xml',
    '*.cover',
    '.hypothesis/',
    '.pytest_cache/',
    '',
    '# Translations',
    '*.mo',
    '*.pot',
    '',
    '# Django stuff:',
    '# *.log',
    'local_settings.py',
    'db.sqlite3',
    '',
    '# Flask stuff:',
    'instance/',
    '.webassets-cache',
    '',
    '# Scrapy stuff:',
    '.scrapy',
    '',
    '# Sphinx documentation',
    'docs/_build/',
    '',
    '# PyBuilder',
    'target/',
    '',
    '# Jupyter Notebook',
    '.ipynb_checkpoints',
    '',
    '# pyenv',
    '.python-version',
    '',
    '# celery beat schedule file',
    'celerybeat-schedule',
    '',
    '# SageMath parsed files',
    '*.sage.py',
    '',
    '# Environments',
    '.env',
    '.venv',
    'env/',
    'venv/',
    'ENV/',
    'env.bak/',
    'venv.bak/',
    '',
    '# Spyder project settings',
    '.spyderproject',
    '.spyproject',
    '',
    '# Rope project settings',
    '.ropeproject',
    '',
    '# mkdocs documentation',
    '/site',
    '',
    '# mypy',
    '.mypy_cache/',
    '',
    '# private',
    '*private*',
    '',
    'package.py',
    '.qaviton_package_manager_cache',
    '.qaviton_package_manager_cache.errors',
    'test_report.xml',
    '',
]
