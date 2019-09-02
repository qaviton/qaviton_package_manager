from subprocess import run as run_block, Popen, PIPE, CalledProcessError
from sys import executable


def escape(string):
    """escape double quote"""
    s = []
    add = s.append
    i = 0
    size = len(string)
    while i < size:

        # ignore back slashes and the char after them
        if string[i] == '\\':
            while i < size:
                add(string[i])
                i += 1

                if string[i] != '\\':
                    add(string[i])
                    i += 1
                    break

        # avoid double quotes
        elif string[i] == '"':
            add('\\')
            add(string[i])
            i += 1

        else:
            add(string[i])
            i += 1

    return "".join(s)


def bs(value: bytes):
    """bytes to string converter"""
    return str(value)[2:-1]


def run(*args) -> bytes:
    command = ' '.join(args)
    try:
        r = run_block(command, shell=True, stdout=PIPE, check=True)
    except CalledProcessError as e: raise OSError(
        f'{command} failed\n'
        f'{e.stderr}, Exit Code: {e.returncode}\n')
    if r.stderr: raise OSError(
        f'{command} failed\n'
        f'{r.stderr}, Exit Code: {r.returncode}\n')
    return r.stdout


def runIO(*args) -> Popen:
    """https://stackoverflow.com/questions/16071866/non-blocking-subprocess-call
    p = runIO("command")
    while p.poll() is None:
        ...
    p.stdout
    p.stderr
    """
    command = ' '.join(args)
    return Popen(command, shell=True, stdout=PIPE)


def python(*args):
    return run(executable, *args)


def pythonC(*args):
    return run(executable, '-c', f'"{escape(";".join(args))}"')


def pythonCIO(*args):
    return runIO(executable, '-c', f'"{escape(";".join(args))}"')


def pytest(*args):
    return run(executable, '-m', 'pytest', *args)
