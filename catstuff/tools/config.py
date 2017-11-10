import yaml


def load_config(path):
    try:
        return yaml.load(open(path, 'r'))
    except yaml.YAMLError as e:
        print("Error trying to load {path}: {error}".format(path=path, error=e))