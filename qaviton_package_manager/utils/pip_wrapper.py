from qaviton_package_manager.utils.system import run
from sys import executable as python


class PIP:
    """wrapper around pip"""
    def __init__(pip): pip.version = pip('--version')
    def __call__(pip, *args): return run(python, '-m', 'pip', *args)
    def install(pip, *args): return pip('install', *args)
    def uninstall(pip, *args): return pip('uninstall', *args, '-y')
    def freeze(pip, filename, *args): return pip('freeze', '>', filename, *args)


pip = PIP()
__all__ = ['pip']
