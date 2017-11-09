def merge(*dicts):
    '''
    Recursively merge dictionaries. If a dictionary contains subdicts, then merge subdicts
    The {**dict1, **dict2} implementation method replaces subdicts rather than merge
    :param dicts: Set of dicts to merge, preferably the last dict
    :return:
    '''

    out = {}

    for d in dicts:
        for key in d:
            if isinstance(out.get(key), dict) and isinstance(d[key], dict):  # if key exists and is a subdict
                out[key] = merge(out[key], d[key])
            elif isinstance(out.get(key), list) and isinstance(d[key], list):
                out[key].append(d[key])
            else:
                out[key] = d[key]
    return out
