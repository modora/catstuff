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


def print_methods(obj):
    """
    Prints all non-private attributes methods (does not start with '_' and not method)
    :param obj:
    :return:
    """
    for attr in dir(obj):
        if attr[0] is "_" or not callable(getattr(obj,attr)):
            continue
        print(attr, ":", getattr(obj, attr))


def print_attr(obj):
    """
    Prints all non-private attributes
    :param obj:
    :return:
    """
    for attr in dir(obj):
        if attr[0] is "_":
            continue
        print(attr, ":", getattr(obj, attr))