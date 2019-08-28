from urllib.parse import quote_plus as urlencode
from qaviton_package_manager.utils.pip_wrapper import pip
from qaviton_package_manager import Manager


def test_pip_install(username="", password=""):
    credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
    package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git@master"
    pip.install(package)
    pip.uninstall('qaviton_package_manager')


def test_create_setup():
    m = Manager()
    m.create('my_test_manager')
