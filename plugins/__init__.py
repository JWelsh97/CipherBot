import inspect
from os import listdir
from os.path import dirname
from importlib import import_module
from cipher.irc import Plugin


plugins = []

for module in listdir(dirname(__file__)):
    module = module.replace('.py', '')
    if module not in ['example', '__pycache__', '__init__']:
        plugin = import_module('.' + module, 'plugins')
        plugins += list(filter(lambda x: x[0] != 'Plugin' and issubclass(x[1], Plugin),
                               inspect.getmembers(plugin, inspect.isclass)))
