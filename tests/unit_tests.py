import os
from urllib.parse import quote_plus as urlencode
from qaviton_package_manager import pip_wrapper
from qaviton_package_manager.create_setup import create_setup


def test_pip_install(username="", password=""):
    credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
    package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git"
    pip_wrapper.install(package)
    pip_wrapper.uninstall('qaviton_package_manager')


# def test_create_setup(username="", password=""):
#     os.getcwd()
#     credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
#     package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git"
#     pip_wrapper.install(package)
#     pip_wrapper.uninstall('qaviton_package_manager')
