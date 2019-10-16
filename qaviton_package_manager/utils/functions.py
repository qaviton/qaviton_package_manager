import os
import shutil
import socket
from contextlib import closing
from qaviton_processes import python
from qaviton_package_manager.conf import SETTINGS, invalid_package_chars, version_specifiers


def get_requirements(root): return root + os.sep + SETTINGS.REQUIREMENTS
def get_test_requirements(root): return root + os.sep + SETTINGS.REQUIREMENTS_TESTS
def normalize_package_name(name): return name.replace('_', '-').replace('.', '-').lower()


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
    if package == requirement:
        return True
    if requirement.startswith(package):
        requirement_specifier = requirement[len(package):len(package)+1]
        for specifier in version_specifiers:
            if requirement_specifier == specifier:
                return True


def get_package_name_from_requirement(requirement: str):
    version = None
    name = requirement
    for i, c in enumerate(requirement):
        if c in invalid_package_chars:
            name = requirement[:i]
            for i, c in enumerate(requirement, start=i):
                if c not in invalid_package_chars:
                    version = requirement[i:]
                    break
            break
    return name, version
