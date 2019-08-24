import subprocess


class RepoData:
    def __init__(self):
        self.username: bytes = None
        self.useremail: bytes = None
        self.url: bytes = None

        git_config = subprocess.run('git config --list', shell=True, stdout=subprocess.PIPE, check=True)
        if git_config.stderr: raise OSError(
            'git config --list failed\n'
            f'{git_config.stderr}, Exit Code: {git_config.returncode}\n'
            'make sure git is installed correctly in this environment:\n'
            'https://git-scm.com/book/en/v2/Getting-Started-Installing-Git')
        self._get_variables(git_config)

    def _get_variables(self, git_config):
        usernameError = OSError(
            'git config --list is missing a user.name\n'
            'please make sure to configure a git username, example:\n'
            'git config user.name "Mona Lisa"'
        )
        useremailError = OSError(
            'git config --list is missing a user.email\n'
            'please make sure to configure a git username, example:\n'
            'git config user.email "mona.lisa@gmail.com"'
        )
        urlError = OSError(
            'git config --list is missing a remote.origin.url\n'
            'please make sure to configure a git username, example:\n'
            'git config remote.origin.url "https://github.com/username/project.git"'
        )
        for line in git_config.stdout.split(b'\n'):
            if line.startswith(b'user.name'):
                try: self.username = line.split(b'=', 1)[1]
                except: raise usernameError

            elif line.startswith(b'user.email'):
                try: self.useremail = line.split(b'=', 1)[1]
                except: raise useremailError

            elif line.startswith(b'remote.origin.url'):
                try:
                    self.url = line.split(b'=', 1)[1]
                    if self.url and self.useremail and self.username:
                        break
                except:
                    raise urlError
        if not self.username: raise usernameError
        if not self.useremail: raise useremailError
        if not self.url: raise urlError
