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


from qaviton_package_manager.utils.git_wrapper import Git


class Build:
    def __init__(self, package_name, to_branch='build', version=None):
        git = Git()
        git.stash()
        git.fetch()
        local_branches = git.get_local_branches()
        remote_branches = [branch.split(b'/', 1)[1] for branch in git.get_remote_branches()]
        current_branch = git.get_current_branch()
        if to_branch not in local_branches:
            git.create_branch(to_branch)
            git.create_remote()
        subbranches = [branch[len(to_branch)+1:] for branch in remote_branches if branch.startswith(bytes(to_branch, 'utf-8')+b'/')]

Build('k')