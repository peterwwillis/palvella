
import importlib, pkgutil

from webrunit.lib.logging import logging as logging
import webrunit.plugins.lib.job

def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

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
        for finder, name, ispkg in iter_namespace(webrunit.plugins.lib.job):
            plugins[name] = importlib.import_module(name)

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug("Found Job type '%s', returning object '%s'" % (plugin_ref.type, plugin_ref))
                    return plugin_ref.classref(**kwargs)
            raise Exception("No such Job type '%s'" % kwargs['type'])

        return Job(**kwargs)

    def run(self, **kwargs):
        logging.debug("Job.run(%s)" % kwargs)
        for action in self.actions:
            logging.debug("  action %s" % action)
