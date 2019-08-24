#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


""" updating pip version:
    ---------------------
1) increase qaviton.version.__version__
2) make sure these are installed:
    pip install wheel
    python setup.py bdist_wheel --universal
    pip install twine
3) run these:
    python setup.py sdist
    python setup.py bdist_wheel
    twine upload dist/*
"""


from sys import version_info
from qaviton_package_manager import __author__, __version__, __author_email__, __description__, __url__, __license__
from setuptools import setup, find_packages


with open("requirements.txt") as f:
    requirements = f.read().splitlines()


with open("README.md") as f:
    long_description = f.read()


setup(
    name="qaviton_package_manager",
    version=__version__,
    author=__author__,
    author_email=__author_email__,
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=__url__,
    packages=[pkg for pkg in find_packages() if pkg.startswith("qaviton_package_manager")],
    license=__license__,
    classifiers=[
        f"Programming Language :: Python :: {'.'.join(version_info()[:2])}",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements
)
