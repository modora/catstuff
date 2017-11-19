import catstuff.core.actions.plugins
import catstuff.core.actions.plugins.parser

__version__ = '1.0'


def print_versions(args):
    # version_list = [
    #     ('Plugin Manager', catstuff.core.actions.plugins.__version__),
    #     ('Parser', catstuff.core.actions.plugins.parser.Parser.__version__),
    #     ('List', catstuff.core.actions.plugins.parser.ListParser.__version__),
    #     ('Version', catstuff.core.actions.plugins.parser.VersionParser.__version__)
    # ]

    version_list = [
        ('Plugin Manager', '1.0'),
        ('Parser', '1.0'),
        ('List', '1.0'),
        ('Version', '1.0')
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
