import os


def expandpath(path):
    '''Expands the variables in the path and return the absolute path'''

    func = [
        os.path.expandvars,
        os.path.expanduser,
        os.path.realpath,
        os.path.abspath
    ]

    for f in func:
        path = f(path)

    return path
