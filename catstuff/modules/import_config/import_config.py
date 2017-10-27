import catstuff.tools.config
import os

class ImportConfig:
    required_args = ('name')
    def __init__(self, **import_args):
        for req in self.required_args:
            if req not in import_args:
                raise KeyError('Missing required argument: {}'.format(req))

        self.name = import_args.get('name')

        # dir options
        self.include = import_args.get('include')
        self.exclude = import_args.get('exclude')
        self.depth = import_args.get('depth')
        self.follow_links = import_args.get('follow_links', False)
        self.default_action = import_args.get('default_action', False)

        # file options
        # none right now

        self.validate_options()

    def validate_options(self):
        if not isinstance(self.name, str):
            assert "Path must be a name"
        if not os.path.isabs(self.name):
            assert "Path must be absolute"

    def get_path_list(self):
        return catstuff.tools.config.import_path_list(
            self.name, include=self.include, exclude=self.exclude,
            max_depth=self.depth, follow_links=self.follow_links,
            default_action=self.follow_links
        )

    def get_imports(self):


def import_config(**import_options):
    name = import_options.get('name')


    if name is None:
        raise KeyError('Missing parameter: ')
