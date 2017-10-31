import os
import fnmatch, collections
import yaml

def expandpath(path):
    """
    Expands the variables in the path and return the absolute path
    :param path:
    :return:
    """

    func = [
        os.path.expandvars,
        os.path.expanduser,
        os.path.realpath,
        os.path.abspath
    ]

    for f in func:
        path = f(path)

    return path


def path_filter(path, include=None, exclude=None, mode='whitelist'):
    """
    Determines whether the path specified matches the criteria specified
    :param file_path:
    :param include:
    :param exclude:
    :param mode:
    :return:
    """
    if mode is 'whitelist':
        # Include if in include and not in exclude, return True
        assert isinstance(include, (collections.Iterable, type(None)))
        assert isinstance(exclude, (collections.Iterable, type(None)))

        # preformatting -- generate of set of all items in include and exclude (if defined)
        include = {
            type(None): lambda x: {'*'},
            str: lambda x: {x},
        }.get(type(include), lambda x: set(x))(include)

        exclude = {
            type(None): lambda x: set(),
            str: lambda x: {x},
        }.get(type(exclude), lambda x: set(x))(exclude)

        for exc in exclude:
            if fnmatch.fnmatchcase(os.path.basename(path), exc):
                for inc in include:
                    if fnmatch.fnmatchcase(os.path.basename(path), inc):
                        return False
        return True
    elif mode is 'blacklist':
        # Include if in include and not in exclude, return True
        assert isinstance(include, (collections.Iterable, type(None)))
        assert isinstance(exclude, (collections.Iterable, type(None)))

        # preformatting
        include = {
            type(None): lambda x: set(),
            str: lambda x: {x},
        }.get(type(include), lambda x: set(x))(include)

        exclude = {
            type(None): lambda x: {'*'},
            str: lambda x: {x},
        }.get(type(exclude), lambda x: set(x))(exclude)

        for inc in include:
            if fnmatch.fnmatchcase(os.path.basename(path), inc):
                for exc in exclude:
                    if fnmatch.fnmatchcase(os.path.basename(path), exc):
                        return True
        return False
    else:
        raise NotImplementedError("Unknown mode: {}".format(mode))


def import_file_list(top, max_depth=0, followlinks=False,
                     include=None, exclude=None, mode='whitelist',
                     safe_walk=True):
    """
    Returns a list of all file paths that match specified options
    :param top: file/parent folder to search
    :param max_depth: maximum search depth (default = 0)
    :param followlinks:
    :param include:
    :param exclude:
    :param mode:
    :param safe_walk: controls safety settings for os.walk (currently only max_depth)

    If safe_walk is enabled, then the max depth is set to at most a default_max_depth
    :return:
    """

    default_max_depth = 8

    filelist = []
    if os.path.isfile(top):
        filelist.append(top) if path_filter(top, include=include, exclude=exclude, mode=mode) else None
        return filelist
    # top is dir
    assert isinstance(max_depth, int)
    if max_depth < 0:
        max_depth = 64  # shouldn't expect anything much more

    if safe_walk:
        max_depth = min(default_max_depth, max_depth)

    prev_dirs = set()  # used to detect cyclic dirs (occurs if follow symlink)

    depth_offset = top.rstrip(os.path.sep).count(os.path.sep)
    for root, dirs, files in os.walk(top, followlinks=followlinks):
        depth = root.rstrip(os.path.sep).count(os.path.sep) - depth_offset

        if followlinks:
            # check to see if we've been in this directory before
            if os.path.realpath(root) in prev_dirs:
                del dirs[:]
                continue
            prev_dirs.union({os.path.realpath(dir) for dir in dirs})

        if depth == max_depth:
            del dirs[:]
        # When mode is blacklist, this will exclude all subdirs so for now, include/exclude only apply to files
        # for i, dir in enumerate(dirs):
        #     if not path_filter(dir, include=include, exclude=exclude, mode=mode):
        #         del dirs[i]
        for file in files:
            f = os.path.join(root, file)
            if path_filter(f, include=include, exclude=exclude, mode=mode):
                filelist.append(f)
    return filelist


class ExplicitDumper(yaml.SafeDumper):
    """
    A dumper that will never emit aliases. -- Found from pyyaml ticket #91
    Usage: yaml.dump(..., Dumper=ExplicitDumper)
    """
    def ignore_aliases(self, data):
        return True


def print_vars(obj):
    """
    Prints all non-private attributes variables (does not start with '_' and not method)
    :param obj:
    :return:
    """
    for attr in dir(obj):
        if attr[0] is "_" or callable(getattr(obj,attr)):
            continue
        print(attr, ":", getattr(obj, attr))
