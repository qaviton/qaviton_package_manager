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
    from setuptools import setup, find_packages
    with open("requirements.txt") as f: requirements = f.read().splitlines()
    with open("README.md", encoding="utf8") as f: long_description = f.read()
    setup(
        name=package_name,
        version="2019.9.23.8.2.27.104341",
        author="Qaviton",
        author_email="info@qaviton.com",
        description="a package manager for git projects with private repositories",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/qaviton/qaviton_package_manager",
        packages=[pkg for pkg in find_packages() if pkg.startswith(package_name)],
        entry_points={"console_scripts": [f"qpm={package_name}.cli:cli"]},
        license="apache-2.0",
        classifiers=[
            f"Programming Language :: Python :: {v[0]}.{v[1]}",
            "Operating System :: OS Independent",
        ],
        install_requires=requirements,
        python_requires='!=2.*,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*',
    )
































