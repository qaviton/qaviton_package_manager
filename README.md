# Qaviton Package Manager
![logo](https://www.qaviton.com/wp-content/uploads/logo-svg.svg)  
[![version](https://img.shields.io/pypi/v/qaviton_package_manager.svg)](https://pypi.python.org/pypi)
[![license](https://img.shields.io/pypi/l/qaviton_package_manager.svg)](https://pypi.python.org/pypi)
[![open issues](https://img.shields.io/github/issues/qaviton/qaviton_package_manager)](https://github/issues-raw/qaviton/qaviton_package_manager)
[![downloads](https://img.shields.io/pypi/dm/qaviton_package_manager.svg)](https://pypi.python.org/pypi)
![code size](https://img.shields.io/github/languages/code-size/qaviton/qaviton_package_manager)
-------------------------  
  
Tired of redundant packaging systems for your software?  
we can package everything using git tags:
```
>qpm --build
         |
branch: dev
         |
branch: tests
         |  
[tag 2019.9.1] 
         |
[tag 2019.9.2]
         |
branch: release/latest


>qpm --install "git+https://url/owner/project.git@release/latest#egg=package:>=2019.9.2"
  |       |      |   |           |                     |             |              |
qaviton install vcs+protocol://project_url          @branch   #egg=package      (optional) 
package method  type                                              directory   pep-440 pep-508
manager                                                             path     :version_specifier
```  

  
## Installation  
```sh  
pip install --upgrade qaviton_package_manager
```  

### Requirements
- git 2.16+  
- Python 3.6+  
  
## Features  
* CI CD workflow ✓  
* managing private+public packages ✓  
* managing nested private packages ✓  
* cli + scripting ✓  
* pip capabilities ✓  
* git capabilities ✓  
* pypi capabilities ✓  
* automatic builds ✓  
* secure credentials ✓  
* cross-platform ✓  
* nested sub-packages ✓  
* nested/multiple packages ✗  
* pip -e installs ✗ (coming soon)  
* docker build ✗ (but can be used with the run function)  
* docker push ✗ (but can be used with the run function)  
  
## Usage  
  
#### creating a manager:  
```
(venv) windows> qpm ^
--create ^
--url "https://github.com/owner/project.git" ^
--username "user1" ^
--password "pass@#$" ^
--email "awsome@qaviton.com" ^
--pypi_user "supasayajin" ^
--pypi_pass "final space" 
```  
```bash
(venv) bash$ qpm  \
--create  \
--url "https://github.com/owner/project.git"  \
--username "user1"  \
--password "pass@#$"  \
--email "awsome@qaviton.com"  \
--pypi_user "supasayajin"  \
--pypi_pass "final space"  \
/
```  
this should leave you with the following project structure:
```
project/
  ├ package/
  │   └ __init__.py  # with __author__, __version__, __author_email__, __description__, __url__, __license__
  ├ tests/
  │   └ __init__.py
  ├ .gitignore
  ├ LICENSE 
  ├ README.md
  ├ requirements.txt
  ├ requirements-test.txt
  ├ setup.py
  └ package.py  # ignored by .gitignore
```
now let's build a package:  
```python
# package.py
from qaviton_package_manager import Manager
from qaviton_package_manager import decypt

# if this is not secure enough, you can add cache_timeout=3600 
# and store credentials in memory
# manager = Manager(cache_timeout=3600)  
# and we need to insert the credentials in run time: > python package.py --username "x"  --password "z"
manager = Manager(**decypt(
    key=b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
    token=b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
))


if __name__ == "__main__":
    # running with lambdas will protect you from processes getting stuck
    manager.run(
        lambda: manager.update(), # pip install -r requirements.txt --upgrade
        lambda: manager.update_test(), # pip install -r requirements-test.txt --upgrade
        lambda: manager.test(), # python -m pytest --junitxml=test_report.xml tests
        lambda: manager.build(), # git commit, tag & push (internal logic is more complicated)
        lambda: manager.upload(), # upload to pypi
    )

```  
make sure you have at list 1 passing test for your package 
```python
# tests/my_package_test.py
def test_with_100p_coverage():
    print("testing my package!\nPASS")
```
```bash
# we can now create a package
python package.py
```  
  
#### CLI:  
we can call any method and send any parameter to the manager through cli:
```bash
# release a version if all tests pass
qpm --username "" --password "" --update --update_test --test --build --upload

# build a stable version if all tests pass
qpm --username "" --password "" --update --update_test --test --build "stable/latest"

# install cachetools using pip and save the requirement in requirements.txt
qpm --install cachetools

# cache credentials in memory
qpm --username "" --password "" --cache_timeout "-1"

# using the system & python to execute tests
qpm --test "system" "echo success" --test "python" "-c" "print(\"py success\");"
```  
  
#### Script:  
```python
# ci_cd.py
from qaviton_processes import run, escape, python
from package import manager
from datetime import datetime


d = datetime.utcnow()
docker_url = manager.vars['docker_url']
docker_user = manager.vars['docker_user']
docker_pass = manager.vars['docker_pass']
docker_email = manager.vars['docker_email']
SSH_PRIVATE_KEY = manager.kwargs['SSH_PRIVATE_KEY']
docker_tag = manager.kwargs['docker_tag']
branch_build = "ci_cd/latest"
dev_branch = "dev"

manager.run(
    lambda: manager.should_build(from_branch=dev_branch, to_branch=branch_build),
    lambda: manager.install(),
    lambda: manager.install_test(),
    lambda: manager.test.pytest("tests/ci_cd"),
    lambda: manager.build(to_branch=branch_build, version=f'{d.year}.{d.month}.{d.day}'),
    # docker distribute
    lambda: run(f"docker login --username=\"{escape(docker_user)}\" --password=\"{escape(docker_pass)}\" --email=\"{escape(docker_email)}\" \"{escape(docker_url)}\""),
    lambda: run(f"docker build --force-rm -t test-multi-stage-builds --build-arg SSH_PRIVATE_KEY=\"{escape(SSH_PRIVATE_KEY)}\" ."),
    lambda: run(f"docker tag {docker_tag} yourhubusername/verse_gapminder:firsttry"),
    lambda: run("docker push yourhubusername/verse_gapminder"),
    # deploy script
    lambda: python("deploy.py")    
)
```
```python
# schedualer.py
from time import time, sleep
from datetime import datetime, timedelta
from qaviton_processes import python_code_async

d = datetime.utcnow()
date = datetime(year=d.year, month=d.month, day=d.day, hour=22)
delta = timedelta(days=1)

# build a package once a day at 22pm
while True:
    python_code_async('import ci_cd')
    date += delta
    sleep(date.timestamp()-time())
    
```  
  
  
## warnings  
* this manager is meant for automated ci cd purposes  
and should not be used instead of regular git commit/push/merge.  
make sure to avoid using it on unstable branches  
to avoid failed packaging requests or potential data loss.  
we recommend using it from a CI CD dedicated branch.  
  
* the manager defaults to encrypted credentials,  
if encrypted credentials on the disk are not secure enough,  
please make sure to enable caching, to store credentials in memory  
