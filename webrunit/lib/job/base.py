import logging

import webrunit
import webrunit.plugins.lib.job

import importlib, pkgutil
def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

discovered_plugins = {}

class Job(object):

    def __init__(self, **kwargs):
        logging.debug("Job.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object and return it;
            otherwise return this object.
        """
        logging.debug("Job.init(%s)" % kwargs)
        plugins = {}
        for k, v in discovered_plugins.items():
            plugins[k] = v.init()

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                bleh = plugin_ref()
                if kwargs['type'] == bleh.type:
                    logging.debug("Found Job type '%s', returning object '%s'" % (bleh.type, plugin_ref))
                    return plugin_ref(**kwargs)
            raise Exception("No such Job type '%s'" % kwargs['type'])

        return Job(**kwargs)

    def run(self, **kwargs):
        logging.debug("Job.run(%s)" % kwargs)
        for action in self.actions:
            logging.debug("  action %s" % action)

discovered_plugins = {
    name: importlib.import_module(name) for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.job)
}
