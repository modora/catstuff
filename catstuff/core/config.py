import catstuff.tools as tools


class CSConfig(tools.config.Config):
    default_path = '~/.conf/catstuff.yml'

    @classmethod
    def load_default(cls):
        return cls.load_config(tools.path.expandpath(cls.default_path))
