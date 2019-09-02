# qaviton_package_manager
-------------------------
  
Tired of redundant packaging systems for your software?  
qaviton is here to help!  
we can package everything into git branches  
  
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
```bash
python -m qaviton_package_manager --create
enter your git username:
enter your git password:
enter your pypi username:
enter your pypi password:
```  
  
now let's build a package:  
```python
# package/manage.py
from qaviton_package_manager import Manager
from package.cred import url, email, username, password, pypi_user, pypi_pass


manager = Manager(
    url=url,
    email=email,
    username=username,
    password=password,
    pypi_user=pypi_user,
    pypi_pass=pypi_pass,
)


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        lambda: manager.build(to_branch='release/latest'),
        # lambda: manager.upload(), # only for pypi public packages (you can uncomment if you understand the implications)
    )
```  
```bash
python package/manage.py
```  
  
  
  
  
  