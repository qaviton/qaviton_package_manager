from urllib.parse import quote_plus as urlencode
import qaviton_package_manager


def test_pip_install(username="", password=""):
    credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
    package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git"
    qaviton_package_manager.install(package)
    qaviton_package_manager.uninstall('qaviton_package_manager')

