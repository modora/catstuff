from catstuff.core.actions.plugins import __version__ as manager_version
from catstuff.core.actions.plugins.list import __version__ as list_version
import catstuff.core.actions.plugins.parser  # avoid using from...import to avoid cyclic import

__version__ = '1.0'


def print_versions():
    version_list = [
        ('PluginManager', manager_version),
        ('Parser', catstuff.core.actions.plugins.parser.__version__),
        ('List', list_version),
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
