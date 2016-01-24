from os import listdir
from os.path import dirname, join
import importlib


for m in listdir(dirname(__file__)):
    if m != '__init__.py':
        m = m.strip('.py')
        if m != 'example':
            importlib.import_module('.' + m, 'plugins')
