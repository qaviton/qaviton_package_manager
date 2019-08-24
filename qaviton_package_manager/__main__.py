from sys import argv
from .create_setup import create_setup


class API:
    create = 'create'
    name = 'name'


def main(**kwargs):
    if API.create in kwargs:
        if API.name in kwargs:
            package_name = kwargs[API.name]
        else:
            package_name = None
        create_setup(package_name)

    if '--'+API.create in argv:
        if '--'+API.name in argv:
            try:
                package_name = argv[argv.index('--'+API.name)+1]
            except:
                raise ValueError("missing name value")
        else:
            package_name = None
        create_setup(package_name)


if __name__ == '__main__':
    main()
