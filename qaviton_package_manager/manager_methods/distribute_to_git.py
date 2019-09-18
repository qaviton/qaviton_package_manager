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


import datetime
from qaviton_helpers import try_to
from qaviton_processes import escape
from qaviton_git import Git
from qaviton_package_manager.manager_methods import Prep
from qaviton_package_manager.utils.functions import get_package_name


class Build(Prep):
    def __init__(self, git: Git, to_branch: str, version: str):
        self.package_name = get_package_name()
        Prep.__init__(self, git, self.package_name)
        version = self.update_version(version)
        branch = f'{to_branch.rsplit("/", 1)[0]}/{version}'
        msg = f'build candidate {branch}'
        git.commit(msg)
        if git.has_remote():
            try:
                git.pull()
            except:
                git.create_remote()
                git.pull()

        local_branches = git.get_local_branches()
        # remote_branches = [branch.split(b'/', 1)[1] for branch in git.get_remote_branches()]
        current_branch = git.get_current_branch()
        if to_branch.encode('utf-8') not in local_branches:
            git.create_branch(to_branch).create_remote()
        elif to_branch != current_branch:
            git.checkout(to_branch)
            git.pull()
            git(f'rebase {current_branch}')

        git.tag(f'{branch}', msg)
        git.push(git.url, to_branch)

        # git.switch(branch).create_remote()
        req = f'git+{git.url}@{branch}#egg={self.package_name}'
        latest = f'git+{git.url}@{to_branch}#egg={self.package_name}'
        print('you can now install this package:')
        print('   1) go to another project with git (make sure you have permissions)')
        print('   2) pip install qaviton_package_manager')
        print('   3) qpm --create --url "x" --username "x" --password "x" --email "x" --pypi_user "x" --pypi_pass "x"')
        print(f'   4) qpm --install "{escape(req)}"')
        print("or if you want the latest version:")
        print(f'   4) qpm --install "{escape(latest)}"')
        try_to(git, f'checkout -f {current_branch}')

    def update_version(self, version):
        version = self.versioning(version)
        with open(self.setup_path, 'rb') as f:
            lines = f.read().splitlines()

        in_setup = False
        for i, line in enumerate(lines):
            if line.strip() == b'setup(':
                in_setup = True
            elif in_setup:
                if line.strip().startswith(b'version'):
                    line = line.split(b'=', 1)
                    line[0] = line[0].rstrip()
                    line[1] = f'"{version}",'.encode("utf-8")
                    lines[i] = b'='.join(line)
                    break

        with open(self.setup_path, 'wb') as f:
            lines.append(b'\n')
            f.write(b'\n'.join(lines))
        return version

    @staticmethod
    def versioning(version):
        if version is None:
            d = datetime.datetime.utcnow()
            version = f'{d.year}.{d.month}.{d.day}.{d.hour}.{d.minute}.{d.second}.{d.microsecond}'
        return version

    @staticmethod
    def versiondate(version: str):
        return datetime.datetime(*[int(t) for t in version.split('.')])
