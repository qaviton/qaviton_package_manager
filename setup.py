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
package_name = "qaviton_package_manager"


if __name__ == "__main__":
    from sys import version_info as v
    from qaviton_package_manager import __author__, __version__, __author_email__, __description__, __url__, __license__
    from setuptools import setup, find_packages
    with open("requirements.txt") as f: requirements = f.read().splitlines()
    with open("README.md", encoding="utf8") as f: long_description = f.read()
    setup(
        name=package_name,
        version=__version__,
        author=__author__,
        author_email=__author_email__,
        description=__description__,
        long_description=long_description,
        long_description_content_type="text/markdown",
        url=__url__,
        packages=[pkg for pkg in find_packages() if pkg.startswith(package_name)],
        license=__license__,
        classifiers=[
            f"Programming Language :: Python :: {v[0]}.{v[1]}",
            "Operating System :: OS Independent",
        ],
        install_requires=requirements
    )
