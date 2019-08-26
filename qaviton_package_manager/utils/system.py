import subprocess


class CompletedProcess(subprocess.CompletedProcess):
    returncode: int
    stdout: bytes
    stderr: bytes


def run(command) -> CompletedProcess:
    r = subprocess.run(command, shell=True, stdout=subprocess.PIPE, check=True)
    if r.stderr: raise OSError(
        f'{command} failed\n'
        f'{r.stderr}, Exit Code: {r.returncode}\n')
    return r
