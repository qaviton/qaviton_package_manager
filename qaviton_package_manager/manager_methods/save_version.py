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
from qaviton_package_manager.utils.functions import create_distibution_packages
from qaviton_package_manager.utils.git_wrapper import Git
from qaviton_package_manager.utils.functions import try_to
from qaviton_package_manager.manager_methods import Prep


class Build(Prep):
    def __init__(self, git: Git, package_name, to_branch='build', version=None):
        Prep.__init__(self, git, package_name)
        version = self.update_version(version)
        branch = f'{to_branch}/{version}'
        msg = f'build candidate {to_branch}/{version}'
        try_to(git.stash)
        try_to(git.commit, msg)
        git.fetch()
        try_to(git.pull)

        local_branches = git.get_local_branches()
        # remote_branches = [branch.split(b'/', 1)[1] for branch in git.get_remote_branches()]
        current_branch = git.get_current_branch()
        if to_branch not in local_branches:
            git.create_branch(to_branch).create_remote()
        elif to_branch != current_branch:
            git.checkout(to_branch)
            try_to(git.stash)
            git.pull()
            git(f'rebase {current_branch}')
        git.tag(f'version {version}', msg)
        git.push(git.url, to_branch)

        git.create_branch(branch)
        try_to(git.create_remote)
        git.push(git.url, branch)
        # TODO: checkout to {to_branch}/{version}
        # TODO: create remote
        # TODO: get git root dir
        # TODO: move dist to root if path is not equal to root+os.sep+dist (if a different dist exists under root delete it first)
        # TODO: remove all directories not starting with .
        # TODO: commit & push
        # TODO: print a comment on how to pip install the version from requirements file
        git.checkout(current_branch)

    def update_version(self, version):
        version = self.versioning(version)
        content = self.get_pkg_init()
        if b'\n__version__' not in content or not content.startswith(b'__version__'):
            raise IOError("missing __version__ in the package __init__.py file")
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(b'__version__'):
                line = line.split(b'=', 1)[1].strip()
                line[1] = version.encode('utf-8')
                lines[i] = b' = '.join(line)
                break
        with open(self.pkg_init, 'wb') as f:
            f.write(b'\n'.join(lines))
        return version

    @staticmethod
    def versioning(version):
        if version is None:
            d = datetime.datetime.utcnow()
            version = f'{d.year}.{d.month}.{d.day}.{d.hour}.{d.min}.{d.second}.{d.microsecond}'
        return version

    @staticmethod
    def versiondate(version: str):
        return datetime.datetime(*[int(t) for t in version.split('.')])
