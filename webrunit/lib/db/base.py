import logging

import webrunit
import webrunit.plugins.lib.db

import importlib, pkgutil
def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

discovered_plugins = {}

class DB(object):

    def __init__(self, **kwargs):
        logging.debug("DB.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object and return it;
            otherwise return this object.
        """
        logging.debug("DB.init(%s)" % kwargs)
        plugins = {}
        for k, v in discovered_plugins.items():
            plugins[k] = v.init()

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                bleh = plugin_ref()
                if kwargs['type'] == bleh.type:
                    logging.debug("Found DB type '%s', returning object '%s'" % (bleh.type, plugin_ref))
                    return plugin_ref(**kwargs)
            raise Exception("No such DB type '%s'" % kwargs['type'])

        return DB(**kwargs)


discovered_plugins = {
    name: importlib.import_module(name) for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.db)
}
