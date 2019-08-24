from pip.__main__ import _main


def install(package, *args):
    """wrapper around pip"""
    _main(['install', package, *args])


def uninstall(package, *args):
    """wrapper around pip"""
    _main(['uninstall', package, *args, '-y'])


def freeze(filename, *args):
    """wrapper around pip"""
    _main(['freeze', '>', filename, *args])
