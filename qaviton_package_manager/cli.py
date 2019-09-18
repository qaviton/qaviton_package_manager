def command_line():
    from os import getcwd, path, sep
    pkg = getcwd()+sep+'package.py'
    if path.exists(pkg):
        manager = __import__(pkg, globals(), locals(), ['manager'], 0)
        manager.run()
        return manager
    else:
        from qaviton_package_manager.__main__ import main
        main()
