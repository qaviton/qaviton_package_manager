import os
import shutil
import socket
from contextlib import closing
from qaviton_package_manager.conf import REQUIREMENTS, REQUIREMENTS_TESTS
from qaviton_package_manager.utils.system import python


def get_requirements(root): return root + os.sep + REQUIREMENTS
def get_test_requirements(root): return root + os.sep + REQUIREMENTS_TESTS


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
