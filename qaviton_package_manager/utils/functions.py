import os
import shutil
import socket
from contextlib import closing
from qaviton_package_manager.conf import REQUIREMENTS
from qaviton_package_manager.utils.pip_wrapper import pip
from qaviton_package_manager.utils.system import python


def get_requirements(root):
    requirements = root + os.sep + REQUIREMENTS
    if not os.path.exists(requirements):
        print(
            f'{REQUIREMENTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS = "filename"')
        name = input(f'select REQUIREMENTS filename({REQUIREMENTS} default):')
        if not name: name = REQUIREMENTS
        requirements = root + os.sep + name
        if not os.path.exists(requirements):
            pip.freeze(requirements)
    return requirements


def try_to(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        return e


def try_or_none(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except:
        return


def clean_distibution():
    shutil.rmtree('build')
    shutil.rmtree('dist')

def create_distibution_packages():
    clean_distibution()
    python('setup.py sdist bdist_wheel --universal')


def upload_to_pypi(username, password):
    create_distibution_packages()
    python(f'-m twine upload -u "{username}" -p "{password}" dist/*')
    clean_distibution()


def get_package_name():
    return python('-c "from setup import package_name;print(package_name)"').decode('utf-8').splitlines()[0]


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def package_match(package, requirement):
    """https://www.python.org/dev/peps/pep-0440/#version-specifiers"""
    if package == requirement \
    or requirement.startswith(package + '=') \
    or requirement.startswith(package + '>') \
    or requirement.startswith(package + '<') \
    or requirement.startswith(package + '~') \
    or requirement.startswith(package + '!'):
        return True
