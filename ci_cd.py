from package import manager


if __name__ == "__main__":
    git = manager.git
    build_branch = 'dev'
    release_branch = 'release/latest'
    working_branch = git.get_current_branch()

    manager.run(
        # lambda: manager.should_build(from_branch=build_branch, to_branch=release_branch),
        # lambda: manager.update(),
        # lambda: manager.update_test(),
        # lambda: manager.test(),
        manager.build(to_branch='dev/latest')
        # lambda: manager.build(release_branch),
        # lambda: manager.upload(),
        # lambda: git.push(),
        # lambda: git.switch('master'),
        # lambda: git.pull(),
        # lambda: git(f'rebase {build_branch}'),
        # lambda: git.push(),
        # lambda: git.switch(working_branch),
    )
