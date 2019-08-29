from urllib.parse import quote_plus as urlencode
from qaviton_package_manager.utils.pip_wrapper import pip
from qaviton_package_manager.utils.git_wrapper import git
from qaviton_package_manager.utils.cache_cred import Cache
from package import manager
import multiprocessing


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


def test_uninstall():
    from sys import argv
    argv.append('--uninstall')
    argv.append('cachetools')
    manager._get_external_args()
    manager.run()


def test_cache():
    timeout = 30
    cache = Cache()
    cache.remove_file()
    server_cached_data = {'username': 'pinki'}
    p = multiprocessing.Process(target=cache.server, args=(timeout,), kwargs=server_cached_data)
    p.start()
    response = cache.client(timeout, cache.method.get, username=True)
    assert response == server_cached_data
    p.join(timeout=timeout)


# if __name__ == "__main__":
#     test_cache()
print(git('config --get user.name'))