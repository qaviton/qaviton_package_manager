import os
from qaviton_package_manager.conf import REQUIREMENTS
from qaviton_package_manager.utils.pip_wrapper import PIP


def get_requirements(root):
    requirements = root + os.sep + REQUIREMENTS
    if not os.path.exists(requirements):
        print(
            f'{REQUIREMENTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS = "filename"')
        name = input(f'select REQUIREMENTS filename({REQUIREMENTS} default):')
        if not name: name = REQUIREMENTS
        requirements = root + os.sep + name
        if not os.path.exists(requirements):
            PIP().freeze(requirements)
    return requirements
