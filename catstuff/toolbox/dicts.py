def merge(*dicts, recursive=True):
    '''
    Recursively merge dictionaries. If a dictionary contains subdicts, then merge subdicts
    The {**dict1, **dict2} implementation method replaces subdicts rather than merge
    :param dicts: Set of dicts to merge, preferably the last dict
    :param recursive: bool -- Utilizes python3 merge dict method
    :return:
    '''

    out = {}
    if recursive:

        for d in dicts:
            for key in d:
                if isinstance(out.get(key), dict) and isinstance(d[key], dict):  # if key exists and is a subdict
                    out[key] = merge(out[key], d[key])
                else:
                    out[key] = d[key]
    else:
        for d in dicts:
            out = {**out, **d}
    return out
