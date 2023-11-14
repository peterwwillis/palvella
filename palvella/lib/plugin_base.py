
import asyncio
import sys
import importlib, pkgutil

from .logging import logging

def iter_namespace(ns_pkg):
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

class PluginClass(object):

    def __init__(self, **kwargs):
        logging.debug( "{}.__init__({})".format(self.__class__.__name__,kwargs) )
        self.__dict__.update(kwargs)
        return

    @staticmethod
    def init(**kwargs):
        """ Look for a plugin for this object, and return a new object of that plugin
            with its own class (that inherits this class - or should, anyway).
            Otherwise return this class's object.
        """
        logging.debug( "{}.init({})".format(self.__class__.__name__,kwargs) )
        plugins = {}
        for finder, name, ispkg in iter_namespace(palvella.plugins.lib.frontend):
            plugins[name] = importlib.import_module(name)

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug(
                        "Found {} type '{}', returning object '{}'".format(
                            self.__class__.__name__,
                            plugin_ref.type,
                            plugin_ref
                        )
                    )
                    return plugin_ref.classref(**kwargs)
            raise Exception( "No such {} type '{}'".format(self.__class__.__name__, kwargs['type']) )

    @classmethod
    async def load_plugins(cls, **kwargs):
        """ If this class has a variable 'plugin_namespace', search that namespace
            for modules. If a module has the function 'plugin_init', run it, passing
            any kwargs passed to us.
        """
        logging.debug("load_plugins(): starting")
        module = importlib.import_module(cls.plugin_namespace)

        plugins = {}
        for finder, name, ispkg in iter_namespace( module ):
            logging.debug("Found plugin '{}'".format(name))
            plugins[name] = importlib.import_module(name)

        for plugin_name, plugin_ref in plugins.items():
            if hasattr(plugin_ref, "plugin_init") and callable(plugin_ref.plugin_init):
                logging.debug("Loading plugin {}".format(plugin_name))
                await plugin_ref.plugin_init(**kwargs)
                logging.debug("Done loading plugin {}".format(plugin_name))
            else:
                logging.debug("No attribute 'plugin_init' in plugin {}".format(plugin_name))

