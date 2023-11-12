
import importlib, pkgutil

from ponyans.lib.logging import logging as logging
import ponyans.plugins.lib.action

def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

class Action(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object and return it;
            otherwise return this object.
        """
        logging.debug("Action.init(%s)" % kwargs)
        plugins = {}
        for finder, name, ispkg in iter_namespace(ponyans.plugins.lib.action):
            plugins[name] = importlib.import_module(name)

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug("Found Action type '%s', returning object '%s'" % (plugin_ref.type, plugin_ref))
                    return plugin_ref.classref(**kwargs)
            raise Exception("No such Action type '%s'" % kwargs['type'])

        return Action(**kwargs)

    def run(self, **kwargs):
        print("Action.run(%s)" % kwargs)

