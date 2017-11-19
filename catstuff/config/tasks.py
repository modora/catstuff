from catstuff.tools.config import try_get, ConfigError


def parser(config):
    tasks = []
    for i, task in enumerate(try_get(config, 'tasks', default=[])):
        if isinstance(task, str):
            tasks.append(task)
        elif isinstance(task, dict):
            if len(task.keys()) > 1:
                raise ConfigError("More than 1 task defined in task {}: {}".format(
                    i, set(task.keys())))
            tasks.append(list(task.keys())[0])
