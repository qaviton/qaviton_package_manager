from qaviton_package_manager.utils.system import run
from qaviton_package_manager.utils.logger import log


class Git:
    def __init__(git):
        git.version = git('--version').replace(b'git version ', b'')
        v = git.version.split(b'.')
        if int(v[0]) < 2 or (int(v[0]) == 2 and int(v[1]) < 10):
            raise OSError(f"git version {v[2:-1]} is not supported, please install a newer version:"
                          "\nhttps://git-scm.com/book/en/v2/Getting-Started-Installing-Git")
        if int(v[0]) < 3 and int(v[1]) < 23:
            def switch(git, branch):
                if git.exists(branch):
                    git(f'checkout {branch}')
                else: git(f'checkout -b {branch}')
                return git
            git.switch = switch

    def __call__(git, command):
        return run('git '+command).stdout

    def stash(git): git('stash'); return git
    def fetch(git): git('fetch'); return git
    def pull(git, *args): git('pull '+' '.join(args)); return git
    def push(git, *args): git('push ' + ' '.join(args)); return git
    def exists(git, branch): return bytes(branch, 'utf-8') in git.get_local_branches()
    def switch(git, branch): git(f'switch -c {branch}'); return git
    def url(git)->bytes: return git('config --get remote.origin.url')
    def create_branch(git, name): git(f'checkout -b {name}'); return git
    def create_remote(git): git(f'push -u origin {git.get_current_branch()}'); return git
    def get_config(git)->[bytes]: return git('config --list').splitlines()
    def get_current_branch(git)->bytes: return git('symbolic-ref --short HEAD').strip()
    def get_remote_branches(git)->[bytes]: return [branch.strip() for branch in git('branch -r').splitlines() if b' -> ' not in branch]
    def get_local_branches(git)->[bytes]:
        branches = git('branch').splitlines()
        for i, branch in enumerate(branches):
            branches[i] = branch.strip()
            if branch.startswith(b'* '):
                branch = branch[2:]
                branches[i] = branch
        return branches


class RepoData:
    def __init__(self):
        self.username: bytes = None
        self.useremail: bytes = None
        self.url: bytes = None
        log.info("parsing git config")

        git_config = Git().get_config()
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
        for line in git_config:
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
