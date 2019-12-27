import os

import yaml


def load():
    with open('config.yml', encoding='UTF-8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


class HiddenRepr(str):
    def __repr__(self):
        return '<str with hidden value>'


def _env_var_constructor(loader: yaml.Loader, node: yaml.Node):
    '''Implements a custom YAML tag for loading optional environment variables.
    If the environment variable is set it returns its value.
    Otherwise returns `None`.

    Example usage:
        key: !ENV 'KEY'
    '''
    if node.id == 'scalar':
        value = loader.construct_scalar(node)
        key = str(value)

    else:
        raise TypeError('Expected a string')

    return HiddenRepr(os.getenv(key))


class Config(yaml.YAMLObject):
    yaml_tag = u'!Config'

    def __init__(self, **kwargs):
        for name, value in kwargs:
            setattr(self, name, value)

    def __reload__(self):
        self.__dict__ = load().__dict__

    def __repr__(self):
        return f'<Config {" ".join(f"{key}={repr(value)}" for key, value in self.__dict__.items())}>'


# Add constructors
yaml.FullLoader.add_constructor('!Config', Config.from_yaml)
yaml.FullLoader.add_constructor('!ENV', _env_var_constructor)

# Load the config
config: Config = load()
