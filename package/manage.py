from qaviton_package_manager import Manager
from package.cred import url, email, username, password, pypi_user, pypi_pass


manager = Manager(
    url=url,
    email=email,
    username=username,
    password=password,
    pypi_user=pypi_user,
    pypi_pass=pypi_pass,
)


if __name__ == "__main__":
    manager.run(
        lambda: manager.update(),
        lambda: manager.update_test(),
        lambda: manager.test(),
        # lambda: manager.build(to_branch='release/latest'),
        lambda: manager.build(),
        lambda: manager.upload(),
    )
