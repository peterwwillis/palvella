import logging

import webrunit
import webrunit.plugins.lib.engine

import importlib, pkgutil
def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

discovered_plugins = {}

class Engine(object):

    @staticmethod
    def init(**kwargs):
        plugins = {}
        for k, v in discovered_plugins.items():
            plugins[k] = v.init()
            logging.debug("Engine plugin: k '%s' -> v '%s'" % (k,v))

        logging.debug("Engine.init(kwargs)")

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                bleh = plugin_ref()
                if kwargs['type'] == bleh.type:
                    logging.debug("Found Engine type '%s', returning object '%s'" % (bleh.type, plugin_ref))
                    return plugin_ref(**kwargs)
                else:
                    raise Exception("No such Engine type '%s'" % kwargs['type'])


discovered_plugins = {
    name: importlib.import_module(name) for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.engine)
}
