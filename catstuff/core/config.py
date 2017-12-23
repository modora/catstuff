import catstuff.tools

print(catstuff.tools)
class CSConfig(catstuff.tools.config.Config):
    default_path = '~/.conf/catstuff.yml'

    @classmethod
    def load_default(cls):
        return cls.load_config(catstuff.tools.path.expandpath(cls.default_path))
