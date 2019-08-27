import subprocess
from sys import executable


def run(*args) -> bytes:
    command = ' '.join(args)
    r = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True)
    if r.stderr: raise OSError(
        f'{command} failed\n'
        f'{r.stderr}, Exit Code: {r.returncode}\n')
    return r.stdout


def python(*args):
    return run(executable, *args)


def bs(value: bytes):
    """bytes to string converter"""
    return str(value)[2:-1]


