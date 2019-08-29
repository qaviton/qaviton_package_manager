from urllib.parse import quote_plus as urlencode
from qaviton_package_manager.utils.pip_wrapper import pip
from package import manager


def test_pip_install(username="", password=""):
    credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
    package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git@master"
    pip.install(package)
    pip.uninstall('qaviton_package_manager')


def test_create_setup():
    manager.create('my_test_manager')


def test_install():
    from sys import argv
    argv.append('--install')
    argv.append('cachetools')
    manager._get_external_args()
    manager.run()

test_install()