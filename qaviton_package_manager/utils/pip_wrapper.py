from qaviton_package_manager.utils.system import run
from sys import executable as python


class PIP:
    """wrapper around pip"""
    def __call__(pip, command, *args):
        return run(f'{python} -m pip {command} '+' '.join(args))

    def install(pip, package, *args): return pip('install', package, *args)
    def uninstall(pip, package, *args): return pip('uninstall', package, *args, '-y')
    def freeze(pip, filename, *args): return pip('freeze', '>', filename, *args)
