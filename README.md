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
  
## Usage  
  
first let's create a manager directory:  
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

now let's build a package:  
```python
# package/manage.py
from qaviton_package_manager import Manager
from qaviton_package_manager import decypt


manager = Manager(**decypt(
    key=b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
    token=b'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx==',
))


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        # lambda: manager.build(to_branch='release/latest'),
        lambda: manager.build(),
        lambda: manager.upload(),
    )

```  
```bash
python -m package.manage
```  
  
  
  
  
  