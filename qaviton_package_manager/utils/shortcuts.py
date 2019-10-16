# short-cuts for the first argument
shortcuts = {
    't': 'test',
    'c': 'create',
    'i': 'install',
    'it': 'install_test',
    'u': 'update',
    'ut': 'update_test',
    'cn': 'clean',
    'cnt': 'clean_test',
    'un': 'uninstall',
    'unt': 'uninstall_test',
    'b': 'build',
    'up': 'upload',
    'sb': 'should_build',

    # long short-cuts (no --)
    'test': 'test',
    'create': 'create',
    'install': 'install',
    'install_test': 'install_test',
    'update': 'update',
    'update_test': 'update_test',
    'clean': 'clean',
    'clean_test': 'clean_test',
    'uninstall': 'uninstall',
    'uninstall_test': 'uninstall_test',
    'build': 'build',
    'upload': 'upload',
    'should_build': 'should_build',
}


def short_cut(self, argv, i):
    if argv[i] in shortcuts:
        api = shortcuts[argv[i]]
    else:
        return i
    args = []
    while not i + 1 >= len(argv) and not argv[i + 1].startswith('--'):
        i += 1
        args.append(argv[i])
    self.kwargs[api] = args
    if api not in self._ord:
        self._ord.append(api)
    return i
