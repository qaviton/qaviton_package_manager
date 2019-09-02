from package import manager


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        lambda: manager.build('release/latest'),
        lambda: manager.upload(),
    )
