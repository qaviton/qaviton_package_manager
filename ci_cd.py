from package.manage import manager


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        # lambda: manager.build(to_branch='release/latest'),
        lambda: manager.build(),
        lambda: manager.upload(),
    )
