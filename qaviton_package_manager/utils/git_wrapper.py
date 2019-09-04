import os
# from urllib.parse import quote_plus as urlencode
from qaviton_helpers import try_to, try_or_none
from qaviton_package_manager.utils.system import run, bs
from qaviton_package_manager.utils.logger import log
from qaviton_package_manager.utils.system import escape


def git(*args): return run('git', *args)
def get_root(): return bs(git('rev-parse --show-toplevel')).replace('/', os.sep)[:-2]


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
        username_error = OSError(
            'git config --list is missing a user.name\n'
            'please make sure to configure a git username, example:\n'
            'git config user.name "Mona Lisa"'
        )
        useremail_error = OSError(
            'git config --list is missing a user.email\n'
            'please make sure to configure a git username, example:\n'
            'git config user.email "mona.lisa@gmail.com"'
        )
        url_error = OSError(
            'git config --list is missing a remote.origin.url\n'
            'please make sure to configure a git username, example:\n'
            'git config remote.origin.url "https://github.com/username/project.git"'
        )
        for line in git_config:
            if line.startswith(b'user.name'):
                try: self.username = line.split(b'=', 1)[1]
                except: raise username_error

            elif line.startswith(b'user.email'):
                try: self.useremail = line.split(b'=', 1)[1]
                except: raise useremail_error

            elif line.startswith(b'remote.origin.url'):
                try:
                    self.url = line.split(b'=', 1)[1]
                    if self.url and self.useremail and self.username:
                        break
                except:
                    raise url_error
        if not self.username: raise username_error
        if not self.useremail: raise useremail_error
        if not self.url: raise url_error


# noinspection PyMethodParameters,PyPropertyDefinition,PyPropertyDefinition,PyBroadException
class Git(GitBase):
    """A super light implementation of git api"""

    # # https://git-scm.com/book/tr/v2/Git-on-the-Server-The-Protocols
    # # we only support https authentication at the moment
    remote_protocols = (
        'git://',
        'http://',
        'https://',
        'ssh://',
        'git://',
        'file:///',
        '/',
        '\\',
    )

    remote = 'origin'

    @classmethod
    def clone(
        cls,
        path: str,
        url: str,
        username: str,
        password: str,
        email: str,
        *args,
    ):
        if url.startswith(cls.remote_protocols[2]):
            url = f'{cls.remote_protocols[2]}{username}:{password}@{url[cls.remote_protocols[2]:]}'
        git(f'clone', *args, url, path)
        return cls(
            url=url,
            username=username,
            password=password,
            email=email,
            root=path,
        )

    @classmethod
    def init(
        cls,
        url: str,
        username: str,
        password: str,
        email: str,
        fetch_args: tuple = None,
        pull_args: tuple = None,
    ):
        if url.startswith(cls.remote_protocols[2]):
            url = f'{cls.remote_protocols[2]}{username}:{password}@{url[cls.remote_protocols[2]:]}'
        git('init')
        git('remote add origin', url)
        project = cls(url, username, password, email)

        if fetch_args is None: fetch_args = tuple()
        if pull_args is None: pull_args = tuple()
        project.fetch(*fetch_args)
        project.pull(*pull_args)
        return project

    def __getitem__(git, item):
        return git.__getattribute__(item)

    def __setitem__(git, key, value):
        git.__setattr__(key, value)

    # def __del__(git):
    #     if git.is_credential_helper_enabled():
    #         git.disable_credential_helper()

    def __init__(git, url=None, username=None, password=None, email=None, root=None):
        git.version = git('--version').replace(b'git version ', b'')
        v = git.version.split(b'.')
        if int(v[0]) < 2 or (int(v[0]) == 2 and int(v[1]) < 16):
            raise OSError(f"git version {v[2:-1]} is not supported, please install a newer version:"
                          "\nhttps://git-scm.com/book/en/v2/Getting-Started-Installing-Git")
        # if int(v[0]) < 3 and int(v[1]) < 23:
        #     def switch(git, branch):
        #         if git.exists(branch):
        #             git(f'checkout "{escape(branch)}"')
        #         else: git(f'checkout -b "{escape(branch)}"')
        #         return git
        #     git.switch = switch
        git.set_credential_helper('cache', '--timeout=31536000')
        git.root = root
        git.url = url
        git.username = username
        git.password = password
        git.email = email

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
    def root(git): return git._root
    @property
    def url(git): return git._url
    @property
    def username(git): return git._username
    @property
    def password(git): return git._password
    @property
    def email(git): return git._email

    @root.setter
    def root(git, value):
        if value:
            git._root = value
        else:
            git._root = get_root()

    @url.setter
    def url(git, value):
        if value:
            # git(f'config remote.{git.remote}.url "{escape(url)}"')
            try:
                git(f'remote add {git.remote} "{escape(value)}"')
            except:
                log.info("IGNORED fatal: remote origin already exists.")
                try:
                    git(f'remote set-url {git.remote} "{escape(value)}"')
                except:
                    pass
            git._url = value
        else:
            git._url = try_or_none(git.get_url)

    @username.setter
    def username(git, value):
        if value:
            run(f'echo "username={escape(value)}" | git credential approve')
            # git(f'config --global user.name "{escape(value)}"')
            git._username = value
        else:
            git._username = try_or_none(git.get_username)

    @password.setter
    def password(git, value):
        if value:
            run(f'echo "password={escape(value)}" | git credential approve')
            # git(f'config --global user.password "{escape(value)}"')
            git._password = value
        else:
            git._password = try_or_none(git.get_password)

    @email.setter
    def email(git, value):
        if value:
            run(f'echo "email={escape(value)}" | git credential approve')
            # git(f'config --global user.email "{escape(value)}"')
            git._email = value
        else:
            git._email = try_or_none(git.get_email)

    def set_credential_helper(git, helper, *options):
        git.disable_credential_helper()
        current = git.get_credential_helper()
        if helper not in current:
            git(f"config --global credential.helper '{helper}{' ' + ' '.join(options) if options else ''}'")
        return git

    def can_merge(git, into):
        """we check if the branch we want to send commits to is up to date or not. if current branch is equal to into branch we check if we want to commit"""
        current_branch = git.get_current_branch()
        if current_branch == into: return git.has_commitable_changes()
        for line in git(f'branch --contains {current_branch}').splitlines():
            if line.strip().decode('utf-8') == into:
                return True

    def has_commitable_changes(git): return git('diff')
    def get_credential_helper(git): return git('config --global --get credential.helper').decode('utf-8').splitlines()[0]
    def disable_credential_helper(git): try_to(git, f'config --global --unset credential.helper'); return git
    def get_url(git)->str: return git(f'config --get remote.{git.remote}.url').decode('utf-8').splitlines()[0]
    def get_username(git)->str: return git('config --get user.name').decode('utf-8').splitlines()[0]
    def get_password(git)->str: return git('config --get user.password').decode('utf-8').splitlines()[0]
    def get_email(git)->str: return git('config --get user.email').decode('utf-8').splitlines()[0]
    def get_config(git)->[bytes]: return git('config --list').splitlines()
    def get_current_branch(git)->str: return git('symbolic-ref --short HEAD').decode('utf-8').strip()
    def get_remote_branches(git)->[bytes]: return [branch.strip().split(b' -> ', 1)[0] for branch in git('branch -r').splitlines()]
    def get_local_branches(git)->[bytes]:
        branches = git('branch').splitlines()
        for i, branch in enumerate(branches):
            branches[i] = branch.strip()
            if branch.startswith(b'* '):
                branch = branch[2:]
                branches[i] = branch
        return branches
    def commit(git, msg):
        if git.has_commitable_changes():
            git(f'commit -a -m "{escape(msg)}"')
        return git
    def stash(git): git('stash'); return git
    def fetch(git, *args): git('fetch', *args); return git
    def pull(git, *args): git('pull --rebase', *args); return git
    def push(git, *args): git('push', *args); return git
    def exists(git, branch): return bytes(branch, 'utf-8') in git.get_local_branches()
    def switch(git, branch):
        # git(f'switch -c "{escape(branch)}"'); return git
        if git.exists(branch):
            git(f'checkout "{escape(branch)}"')
        else:
            git(f'checkout -b "{escape(branch)}"')
        return git
    def create_branch(git, name): git(f'checkout -b "{escape(name)}"'); return git
    def create_remote(git, branch=None): git(f'push -u {git.remote} "{escape(git.get_current_branch() if branch is None else branch)}"'); return git
    def checkout(git, to_branch): git(f'checkout "{escape(to_branch)}"'); return git
    def has_remote(git): return git('checkout')
    def delete_remote(git, branch): git(f'push {git.remote} --delete "{escape(branch)}"'); return git
    def delete_local(git, branch): git(f'branch -d "{escape(branch)}"'); return git
    def tag(git, name, msg): git(f'tag -a {name} -m "{escape(msg)}"'); return git
    def add(git, arg='.', *args): git('add -f', arg, *args); return git
