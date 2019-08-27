from urllib.parse import quote_plus as urlencode
from qaviton_package_manager.utils.system import run
from qaviton_package_manager.utils.logger import log


def git(*args): return run('git ' + ' '.join(args)).stdout


class GitBase:
    def __call__(self, *args):
        return git(*args)
    @staticmethod
    def get_config()->[bytes]: return git('config --list').splitlines()


class RepoData:
    def __init__(self):
        self.username: bytes = None
        self.useremail: bytes = None
        self.url: bytes = None
        log.info("parsing git config")

        git_config = GitBase.get_config()
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


class Git(GitBase):
    def __init__(git, url, username='', password=''):
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

        git.url = url
        git.username = username
        git.password = password
        # https://git-scm.com/book/tr/v2/Git-on-the-Server-The-Protocols
        # we only support https authentication at the moment
        remote_protocols = (
            # 'git://',
            # 'http://',
            git._https_handler,
            # 'ssh://',
            # 'git://',
            # 'file:///',
            # '/',
            # '\\'
        )
        for protocol in remote_protocols:
            if protocol():
                break

    def _https_handler(git):
        protocol = 'https://'
        if git.url.startswith(protocol):
            if git.username:
                credentials = f'{urlencode(git.username)}:{urlencode(git.password)}@'
            elif git.password:
                credentials = f'{git.password}@'
            else:
                credentials = ''
            git.url = f'{protocol}{credentials}{git.url[len(protocol):]}'
            return True

    def stash(git): git('stash'); return git
    def fetch(git): git('fetch', git.url); return git
    def pull(git): git('pull', git.url); return git
    def push(git): git('push', git.url); return git
    def exists(git, branch): return bytes(branch, 'utf-8') in git.get_local_branches()
    def switch(git, branch): git(f'switch -c {branch}'); return git
    # def url(git)->bytes: return git('config --get remote.origin.url')
    def create_branch(git, name): git(f'checkout -b {name}'); return git
    def create_remote(git): git(f'push -u origin {git.get_current_branch()}'); return git
    def get_config(git)->[bytes]: return git('config --list').splitlines()
    def get_current_branch(git)->bytes: return git('symbolic-ref --short HEAD').strip()
    def get_remote_branches(git)->[bytes]: return [branch.strip().split(b' -> ', 1)[0] for branch in git('branch -r').splitlines()]
    def get_local_branches(git)->[bytes]:
        branches = git('branch').splitlines()
        for i, branch in enumerate(branches):
            branches[i] = branch.strip()
            if branch.startswith(b'* '):
                branch = branch[2:]
                branches[i] = branch
        return branches
