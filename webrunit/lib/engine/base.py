import logging

import webrunit
import webrunit.plugins.lib.engine

import importlib, pkgutil
def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

discovered_plugins = {}

class Engine(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object and return it;
            otherwise return this object.
        """
        logging.debug("Engine.init(%s)" % kwargs)
        plugins = {}
        for k, v in discovered_plugins.items():
            plugins[k] = v.init()

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                bleh = plugin_ref()
                if kwargs['type'] == bleh.type:
                    logging.debug("Found Engine type '%s', returning object '%s'" % (bleh.type, plugin_ref))
                    return plugin_ref(**kwargs)
            raise Exception("No such Engine type '%s'" % kwargs['type'])

        return Engine(**kwargs)

discovered_plugins = {
    name: importlib.import_module(name) for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.engine)
}
