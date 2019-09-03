from qaviton_package_manager.conf import TESTS_DIR
from qaviton_package_manager.utils.system import run, python, pytest


class Test(dict):
    def __call__(self, runner=None, *args):
        if not runner:
            if not args:
                args = ('--junitxml=test_report.xml', TESTS_DIR)
            return pytest(*args)
        if runner not in self:
            raise ValueError(f'{runner} is not a valid test executable')
        return self[runner](*args)

    def __init__(self):
        dict.__init__(self,
            system=run,
            python=python,
            pytest=pytest,
        )
        self.system: run = self['system']
        self.python: python = self['python']
        self.pytest: pytest = self['pytest']
