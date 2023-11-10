
import importlib, pkgutil

from webrunit.lib.logging import logging as logging
import webrunit.plugins.lib.trigger

def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

class Trigger(object):

    def __init__(self, **kwargs):
        logging.debug("Trigger.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object and return it;
            otherwise return this object.
        """
        logging.debug("Trigger.init(%s)" % kwargs)
        plugins = {}
        for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.trigger):
            plugins[name] = importlib.import_module(name)

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug("Found Trigger type '%s', returning object '%s'" % (plugin_ref.type, plugin_ref))
                    return plugin_ref.classref(**kwargs)
            raise Exception("No such Trigger type '%s'" % kwargs['type'])

        return Trigger(**kwargs)

