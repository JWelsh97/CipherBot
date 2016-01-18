import os
import yaml


def read_config():
    """
    Reads the YAML config file
    """
    path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(path, 'config.yaml'), 'r') as f:
        conf = yaml.load(f)
    return conf
