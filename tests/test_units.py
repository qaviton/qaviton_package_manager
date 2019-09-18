# import time
from urllib.parse import quote_plus as urlencode
from qaviton_pip import pip
# from qaviton_git import Git
from qaviton_package_manager.utils.cache_cred import Cache
from package import manager


def test_pip_install(username="", password=""):
    credentials = "" if len(username) + len(password) == 0 else f"{urlencode(username)}:{urlencode(password)}@"
    package = f"git+https://{credentials}github.com/qaviton/qaviton_package_manager.git@master"
    pip.install(package)
    pip.uninstall('qaviton_package_manager')


# def test_create_setup():
#     manager.create('my_test_manager')


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


# def test_cache():
#     server_cached_data = {
#         'username': 'pinki',
#         'password': 'pokol',
#     }
#     cache_timeout = 30
#     cache = Cache()
#     if cache.server_is_alive():
#         cache.kill_server()
#
#     p = cache.create_server(cache_timeout, **server_cached_data)
#     response = cache.get(*server_cached_data.keys())
#     assert response == server_cached_data
#     created = cache.get_file_content()['created']
#     while p.poll() is None:
#         time.sleep(0.3)
#         assert time.time() - created < cache_timeout + 5
#     assert p.returncode == 0
#     if cache.server_is_alive():
#         cache.kill_server()
def test_cache():
    server_cached_data = {
        'dooki': 'pinki',
        'pooki': 'pokol',
    }
    cache = Cache()
    if cache.server_is_alive():
        response = cache.post(**server_cached_data)
        assert response == {}
    else:
        cache_timeout = 30
        cache.create_server(cache_timeout, **server_cached_data)

    response = cache.get(*server_cached_data.keys())
    assert response == server_cached_data

    response = cache.delete(*server_cached_data.keys())
    assert response == {}


# def test_git():
#     git = Git()
#     assert git.url == manager.git.url
#     assert git.username == manager.git.username
#     assert git.password == manager.git.password
#     assert git.email == manager.git.email


def test_cli():
    from package import manager
    from qaviton_package_manager.cli import command_line
    manager.vars['123'] = True
    manager = command_line()
    assert '123' in manager.vars
