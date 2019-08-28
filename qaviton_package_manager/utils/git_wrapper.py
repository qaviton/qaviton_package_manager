import os
from qaviton_package_manager.utils.system import run, bs
from qaviton_package_manager.utils.logger import log
from qaviton_package_manager.utils.functions import escape


def git(*args): return run('git', *args)


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
    def __init__(git, url=None, username=None, password=None):
        git.version = git('--version').replace(b'git version ', b'')
        v = git.version.split(b'.')
        if int(v[0]) < 2 or (int(v[0]) == 2 and int(v[1]) < 16):
            raise OSError(f"git version {v[2:-1]} is not supported, please install a newer version:"
                          "\nhttps://git-scm.com/book/en/v2/Getting-Started-Installing-Git")
        if int(v[0]) < 3 and int(v[1]) < 23:
            def switch(git, branch):
                if git.exists(branch):
                    git(f'checkout "{escape(branch)}"')
                else: git(f'checkout -b "{escape(branch)}"')
                return git
            git.switch = switch

        git.credential_mode = git('config --get credential.helper').decode('utf-8').splitlines()[0]
        git('config credential.helper store')
        git.root = bs(git('rev-parse --show-toplevel')).replace('/', os.sep)[:-2]
        git.url = url

        if username:
            git.username = username
        else:
            git._username = git.get_username()

        if password:
            git.password = password
        else:
            git._password = git.get_password()
        # # https://git-scm.com/book/tr/v2/Git-on-the-Server-The-Protocols
        # # we only support https authentication at the moment
        # remote_protocols = (
        #     # 'git://',
        #     # 'http://',
        #     git._https_handler,
        #     # 'ssh://',
        #     # 'git://',
        #     # 'file:///',
        #     # '/',
        #     # '\\'
        # )
        # for protocol in remote_protocols:
        #     if protocol():
        #         break

    def __del__(git):
        git(f'config --unset credential.helper store')
        if git.password:
            git(f'config --unset user.password "{escape(git.password)}"')

    # def _https_handler(git):
    #     protocol = 'https://'
    #     if git.url.startswith(protocol):
    #         if git.username:
    #             credentials = f'{urlencode(git.username)}:{urlencode(git.password)}@'
    #         elif git.password:
    #             credentials = f'{git.password}@'
    #         else:
    #             credentials = ''
    #         git.url = f'{protocol}{credentials}{git.url[len(protocol):]}'
    #         return True

    @property
    def url(git):
        return git._url

    @url.setter
    def url(git, value):
        if value:
            # git(f'config remote.origin.url "{escape(url)}"')
            try:
                git(f'remote add origin "{escape(value)}"')
            except:
                try:
                    git(f'remote set-url origin "{escape(value)}"')
                except:
                    pass
        git._url = value

    @property
    def username(git):
        return git._username

    @property
    def password(git):
        return git._password

    @username.setter
    def username(git, value):
        if value:
            git(f'config user.name "{escape(value)}"')
        git._username = value

    @password.setter
    def password(git, value):
        if value:
            git(f'config user.password "{escape(value)}"')
        git._password = value

    def commit(git, msg): git(f'commit -m "{escape(msg)}"')
    def stash(git): git('stash'); return git
    def fetch(git, *args): git('fetch', *args); return git
    def pull(git, *args): git('pull --rebase', *args); return git
    def push(git, *args): git('push', *args); return git
    def exists(git, branch): return bytes(branch, 'utf-8') in git.get_local_branches()
    def switch(git, branch): git(f'switch -c "{escape(branch)}"'); return git
    def get_url(git)->bytes: return git('config --get remote.origin.url')
    def get_username(git) -> bytes: return git('config --get user.name')
    def get_password(git) -> bytes: return git('config --get user.password')
    def create_branch(git, name): git(f'checkout -b "{escape(name)}"'); return git
    def checkout(git, to_branch): git(f'checkout "{escape(to_branch)}"'); return git
    def create_remote(git, branch=None): git(f'push -u origin "{escape(git.get_current_branch().decode("utf-8") if branch is None else branch)}"'); return git
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
    def delete_remote(git, branch): git(f'push origin --delete "{escape(branch)}"'); return git
    def delete_local(git, branch): git(f'branch -d "{escape(branch)}"'); return git
    def tag(git, name, msg): git(f'tag -a {name} -m "{escape(msg)}"'); return git
    def add(git, arg='.', *args): git('add -f', arg, *args); return git
