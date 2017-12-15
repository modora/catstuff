from catstuff import core
from . import list as list_version

__version__ = '1.0'


def print_versions():
    version_list = [
        ('PluginManager', core.plugins.CSPluginManager.__version__),
        ('List', list_version.__version__),
        ('Version', __version__)
    ]

    max_lengths = {
        'name': 1,
        'version': 1
    }
    for name, version in version_list:
        max_lengths['name'] = max(len(name), max_lengths['name'])
        max_lengths['version'] = max(len(version), max_lengths['version'])
    for name, version in version_list:
        print(
            "{name:{name_len}}".format(name=name, name_len=max_lengths['name']),
            ":",
            "{version:{ver_len}}".format(version=version, ver_len=max_lengths['version'])
        )


def print_wrapper(args):
    # No args atm
    print_versions()
