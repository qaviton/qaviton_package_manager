import os
from .git_data import RepoData
from .conf import LICENSE, README, REQUIREMENTS
from .pip_wrapper import freeze


class HTTP:
    _session = None
    @staticmethod
    def get():
        if HTTP._session is None:
            import requests
            HTTP._session = requests.Session()
        return HTTP._session


def select_license():
    print('fetching licenses')
    http = HTTP.get()
    r = http.get('https://api.github.com/licenses')
    r.raise_for_status()
    licenses: list = r.json()
    while True:
        print("\nSelect a License:")
        for i, l in enumerate(licenses):
            print(f"  ({i + 1}) {l['key']}")
        try:
            return licenses[int(input("")) - 1]['key']
        except:
            print('invalid input, please select a valid number')


def get_license(root):
    license = root + os.sep + LICENSE
    key = None
    if not os.path.exists(license):
        print(f'{LICENSE} not found\nP.S. you can change the default license filename with qaviton_package_manager.conf.LICENSE = "filename"')
        name = input(f'select LICENSE filename({LICENSE} default):')
        if not name: name = README
        license = root + os.sep + name
        if not os.path.exists(license):
            key = select_license()
            print(f'creating file: {license}')
            http = HTTP.get()
            r = http.get(f'https://api.github.com/licenses/{key}')
            r.raise_for_status()
            content = r.json()['body']
            with open(license, 'w') as f:
                f.write(content)
    return {'file': license, 'key': key}


def get_readme(root, package_name):
    readme = root + os.sep + README
    if not os.path.exists(readme):
        print(f'{README} not found\nP.S. you can change the default readme filename with qaviton_package_manager.conf.README = "filename"')
        name = input(f'select README filename({README} default):')
        if not name: name = README
        readme = root + os.sep + name
        if not os.path.exists(readme):
            print(f'creating file: {readme}')
            with open(readme, 'w') as f:
                f.write(package_name.replace('_', ' '))
    return readme


def get_requirements(root):
    requirements = root + os.sep + REQUIREMENTS
    if not os.path.exists(requirements):
        print(f'{REQUIREMENTS} not found\nP.S. you can change the default requirements filename with qaviton_package_manager.conf.REQUIREMENTS = "filename"')
        name = input(f'select REQUIREMENTS filename({REQUIREMENTS} default):')
        if not name: name = REQUIREMENTS
        requirements = root + os.sep + name
        if not os.path.exists(requirements):
            freeze(requirements)
    return requirements


def get_pkg_init(pkg_path, pkg_init):
    if not os.path.exists(pkg_path):
        print(f"direcotory: {pkg_path} is missing")
        print("creating package...")
        os.mkdir(pkg_path)
        open(pkg_init, 'w').close()
        init = b''
    elif not os.path.exists(pkg_init):
        print(f"file: {pkg_init} is missing")
        print("creating package init file...")
        open(pkg_init, 'w').close()
        init = b''
    else:
        with open(pkg_init, 'rb') as f:
            init = f.read()
    return init


def handle_package_init(
        init_content: bytes,
        repo: RepoData,
        package_name: str,
        license:dict,
        pkg_init):
    missing_init_params = []

    tmp = b'\n' + init_content
    if b'\n__author__' not in tmp:
        print(f'missing __author__ in init file, adding line: __author__ = {str(repo.username)[1:-1]}')
        missing_init_params.append(b'\n__author__ = ' + repo.username)

    if b'\n__version__' not in tmp:
        print(f'missing __version__ in init file, adding line: __version__ = 0.0.1')
        missing_init_params.append(b'\n__version__ = 0.0.1')

    if b'\n__author_email__' not in tmp:
        print(f'missing __author_email__ in init file, adding line: __author_email__ = {str(repo.useremail)[1:-1]}')
        missing_init_params.append(b'\n__author_email__ = ' + repo.useremail)

    if b'\n__description__' not in tmp:
        description = package_name.replace('_', ' ')
        print(f'missing __description__ in init file, adding line: __description__ = {description}')
        missing_init_params.append(b'\n__description__ = ' + bytes(description, 'utf-8'))

    if b'\n__url__' not in tmp:
        print(f'missing __url__ in init file, adding line: __url__ = {str(repo.url)[1:-1]}')
        missing_init_params.append(b'\n__url__ = ' + repo.url)

    if b'\n__license__' not in tmp:
        if license["key"] is None:
            license["key"] = select_license()
        print(f'missing __license__ in init file, adding line: __license__ = {license["key"]}')
        missing_init_params.append(b'\n__license__ = ' + bytes(license["key"], 'utf-8'))

    if missing_init_params:
        missing_init_params.append(b'\n')

    missing_init_params.append(init_content)
    content = b''.join(missing_init_params)
    with open(pkg_init, 'wb') as f:
        f.write(content)


def create_setup_file(package_name, readme, requirements):
    content = b''.join([
        b'from sys import version_info'
        b'from ' + bytes(package_name, 'utf-8') + b' import __author__, __version__, __author_email__, __description__, __url__, __license__\n',
        b'from setuptools import setup, find_packages\n',
        b'\n',
        b'\n',
        b'with open("' + bytes(requirements.rsplit(os.sep, 1), 'utf-8') + b'") as f:\n',
        b'    requirements = f.read().splitlines()\n',
        b'\n',
        b'\n',
        b'with open("' + bytes(readme.rsplit(os.sep, 1), 'utf-8') + b'") as f:\n',
        b'    long_description = f.read()\n',
        b'\n',
        b'\n',
        b'setup(\n',
        b'    name="' + bytes(package_name, 'utf-8') + b'",\n',
        b'    version=__version__,\n',
        b'    author=__author__,\n',
        b'    author_email=__author_email__,\n',
        b'    description=__description__,\n',
        b'    long_description=long_description,\n',
        b'    long_description_content_type="text/markdown",\n',
        b'    url=__url__,\n',
        b'    packages=[pkg for pkg in find_packages() if pkg.startswith("' + bytes(package_name, 'utf-8') + b'")],\n',
        b'    license=__license__,\n',
        b'    classifiers=[\n',
        b'        f"Programming Language :: Python :: {\'.\'.join(version_info()[:2])}",\n',
        b'        "Operating System :: OS Independent",\n',
        b'    ],\n',
        b'    install_requires=requirements\n',
        b')\n',
    ])
    with open('setup.py', 'wb') as f:
        f.write(content)


def create_setup(package_name=None):
    repo = RepoData()
    root = os.getcwd()

    if os.path.exists(root+os.sep+'setup.py'):
        raise FileExistsError("setup.py already exist")

    if package_name is None:
        package_name = root.rsplit(os.sep, 1)[1]
        print('package name not specified, selecting dir name:', package_name)

    pkg_path = root+os.sep+package_name
    pkg_init = pkg_path + os.sep + '__init__.py'

    init_content = get_pkg_init(pkg_path, pkg_init)
    license = get_license(root)
    readme = get_readme(root, package_name)
    requirements = get_requirements(root)

    handle_package_init(init_content, repo, package_name, license, pkg_init)

    create_setup_file(package_name, readme, requirements)
