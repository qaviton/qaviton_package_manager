# qaviton_package_manager
-------------------------
  
Tired of redundant packaging systems for your software?  
qaviton is here to help!  
we can package everything into simple  
  
git branches:  
```
  |
 dev
  |
tests
  |  
release/2019.9.1.21.12.2.127916      
  |
release/2019.9.2.0.39.13.173494     
  |
release/latest
```  
you can now install this package:  
```pip install git+https://github.com/owner/package.git@release/latest```  
  
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
* crossplatform ✓    
  
## Usage  
  
#### creating a manager:  
```
(venv) windows> python -m qaviton_package_manager ^
--create ^
--url "https://github.com/owner/project.git" ^
--username "user1" ^
--password "pass@#$" ^
--email "awsome@qaviton.com" ^
--pypi_user "supasayajin" ^
--pypi_pass "final space" 
```  
```bash
(venv) bash$ python -m qaviton_package_manager  \
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
# package/manage.py
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
```bash
# make sure you have at list 1 passing test for your package 
python package.py
```  
  
#### CLI:  
we can call any method and send any parameter to the manager through cli:
```bash
# release a version if all tests pass
python package.py --username "" --password "" --update --update_test --test --build --upload

# build a stable version if all tests pass
python package.py --username "" --password "" --update --update_test --test --build "stable/latest"

# install cachetools using pip and save the requirement in requirements.txt
python package.py --install cachetools

# cache credentials in memory
python package.py --username "" --password "" --cache_timeout "-1"

# using the system & python to execute tests
python package.py --test "system" "echo success" --test "python" "-c" "print(\"py success\");"
```  
  
#### Script:  
```python
# ci_cd.py
from qaviton_package_manager import run, escape
from package import manager
from datetime import datetime


d = datetime.utcnow()
docker_url = manager.vars['docker_url']
docker_user = manager.vars['docker_user']
docker_pass = manager.vars['docker_pass']
docker_email = manager.vars['docker_email']
SSH_PRIVATE_KEY = manager.kwargs['SSH_PRIVATE_KEY']
docker_tag = manager.kwargs['docker_tag']

manager.run(
    lambda: manager.install(),
    lambda: manager.install_test(),
    lambda: manager.test.pytest("tests/ci_cd"),
    lambda: manager.build(to_branch="ci_cd/latest", version=f'{d.year}.{d.month}.{d.day}'),
    # docker distribute
    lambda: run(f"docker login --username=\"{escape(docker_user)}\" --password=\"{escape(docker_pass)}\" --email=\"{escape(docker_email)}\" \"{escape(docker_url)}\""),
    lambda: run(f"docker build --force-rm -t test-multi-stage-builds --build-arg SSH_PRIVATE_KEY=\"{escape(SSH_PRIVATE_KEY)}\" ."),
    lambda: run(f"docker tag {docker_tag} yourhubusername/verse_gapminder:firsttry"),
    lambda: run("docker push yourhubusername/verse_gapminder"),
    # deploy script
    lambda: run("deploy.py")    
)
```  
  
## not yet supported  
* pip -e installs  
* nested packages (might not get supported)  
* docker build (but can be used with the run function)  
* docker push (but can be used with the run function)  
  
## warnings  
* this manager is meant for automated ci cd purposes  
and should not be used instead regular git commits/pushes  
make sure to avoid using it on unstable branches  
to avoid failed packaging requests or potential data loss.  
we recommend using it from a CI CD dedicated branch.  
  
* the manager defaults to encryped credentials,  
if encrypted credentials on the disk are not secure enough  
please make sure to enable caching, to store credentials in memory  
  