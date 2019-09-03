import os
import shutil
import socket
from contextlib import closing
from qaviton_package_manager.conf import REQUIREMENTS, REQUIREMENTS_TESTS, TESTS_DIR
from qaviton_package_manager.utils.pip_wrapper import pip
from qaviton_package_manager.utils.system import python


def get_requirements(root): return root + os.sep + REQUIREMENTS
def get_test_requirements(root): return root + os.sep + REQUIREMENTS_TESTS


def set_requirements(root):
    requirements = get_requirements(root)
    if not os.path.exists(requirements):
        print(f'{REQUIREMENTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS = "filename"')
        name = input(f'select REQUIREMENTS filename({REQUIREMENTS} default):')
        if not name: name = REQUIREMENTS
        requirements = root + os.sep + name
        if not os.path.exists(requirements):
            pip.freeze(requirements)
    return requirements


def set_test_requirements(root):
    path = root + os.sep + REQUIREMENTS_TESTS
    if not os.path.exists(path):
        print(f'{REQUIREMENTS_TESTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS_TESTS = "filename"')
        name = input(f'select REQUIREMENTS_TESTS filename({REQUIREMENTS_TESTS} default):')
        if not name: name = REQUIREMENTS_TESTS
        path = root + os.sep + name
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('pytest')
    path = root + os.sep + TESTS_DIR
    if not os.path.exists(path):
        print(f'{TESTS_DIR} not found\nP.S. you can change the default tests directory with qaviton_package_manager.conf.TESTS_DIR = "filename"')
        name = input(f'select TESTS_DIR filename({TESTS_DIR} default):')
        path = root + os.sep + name
        if not os.path.exists(path):
            os.mkdir(path)
            open(path+os.sep+'__init__.py').close()


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
    if os.path.exists('build'): shutil.rmtree('build')
    if os.path.exists('dist'): shutil.rmtree('dist')
    if os.path.exists(get_package_name()+'.egg-info'):
        shutil.rmtree(get_package_name()+'.egg-info')


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
