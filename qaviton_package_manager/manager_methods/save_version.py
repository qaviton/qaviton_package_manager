# # Copyright 2019 qaviton.com, Inc. or its affiliates. All Rights Reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License"). You
# # may not use this file except in compliance with the License. A copy of
# # the License is located at
# #
# # https://github.com/qaviton/qaviton_package_manager/blob/master/LICENSE
# #
# # or in the "license" file accompanying this file. This file is
# # distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# # ANY KIND, either express or implied. See the License for the specific
# # language governing permissions and limitations under the License.
# from qaviton_package_manager.utils.git_wrapper import Git
#
import datetime
date = datetime.datetime.utcnow()
print(date)
# class Build:
#     def __init__(self, package_name, to_branch='build', version=None):
#         git = Git()
#         git.stash()
#         git.fetch()
#         local_branches = git.get_local_branches()
#         remote_branches = [branch.split(b'/', 1)[1] for branch in git.get_remote_branches()]
#         current_branch = git.get_current_branch()
#         if to_branch not in local_branches:
#             git.create_branch(to_branch)
#             git.create_remote()
#         if version is None:
#             def sort_best(versions, significance=0):
#                 best = {}
#                 for i, version in enumerate(versions):
#                     if len(version) > significance:
#                         try: v = int(version[significance])
#                         except: continue
#                         if v not in best:
#                             best[v] = [i]
#                         else:
#                             best[v].append(i)
#                 if len(best) == 0:
#                     return None
#                 if len(best) == 1:
#                     for version in best.values():
#                         return version
#                 if len(best) > 1:
#                     version = sort_best(versions=[v for i, v in enumerate(versions) if i in best], significance=significance+1)
#                     if version is None:
#                         for version in best.values():
#                             return version
#             version = sort_best([branch[len(to_branch)+1:].decode('utf-8').split('.') for branch in remote_branches if branch.startswith(bytes(to_branch, 'utf-8')+b'/')])
#             if version is None:
#                 version = '0.0.0.0.1'
#             else:
#                 version[-1] += 1
#                 if len(version) > 3 and version[-1] > 10:
#                     for i in range(-1, -len(version)+2, -1):
#                         version[i] += 1
#                         if version[i] > 10:
#
#                 if len(version) > 2 and version[-1] > 25
#         else:
#             branch = f'{to_branch}/{version}'
#
#     def versioning(self, version: str):
#         pass
#
#
# Build('k')
# for i in range(len([1,1,1,1,1])-1, 3-1, -1):
#     print(i)
#
#
# for i in range(-1, -len([1,1,1,1,1])+3-1, -1):
#     print(i)