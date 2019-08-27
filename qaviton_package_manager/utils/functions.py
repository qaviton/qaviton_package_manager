import os
import shutil
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


def escape(string):
    """escape double quote"""
    s = []
    add = s.append
    i = 0
    size = len(string)
    while i < size:

        # ignore back slashes and the char after them
        if string[i] == '\\':
            while i < size:
                add(string[i])
                i += 1

                if string[i] != '\\':
                    add(string[i])
                    i += 1
                    break

        # avoid double quotes
        elif string[i] == '"':
            add('\\')
            add(string[i])
            i += 1

        else:
            add(string[i])
            i += 1

    return "".join(s)


def try_to(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        return e


def create_distibution_packages():
    shutil.rmtree('build')
    shutil.rmtree('dist')
    python('setup.py sdist bdist_wheel --universal')


def upload_to_pypi(username, password):
    create_distibution_packages()
    python(f'-m twine upload -u "{username}" -p "{password}" dist/*')
