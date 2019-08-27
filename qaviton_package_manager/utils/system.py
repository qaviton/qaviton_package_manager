import subprocess
from sys import executable


class CompletedProcess(subprocess.CompletedProcess):
    returncode: int
    stdout: bytes
    stderr: bytes


def run(*args) -> CompletedProcess:
    command = ' '.join(args)
    r = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True)
    if r.stderr: raise OSError(
        f'{command} failed\n'
        f'{r.stderr}, Exit Code: {r.returncode}\n')
    return r


def python(*args):
    return run(executable, *args)


def bs(value: bytes):
    """bytes to string converter"""
    return str(value)[2:-1]


