
import asyncio  # noqa: F401
import importlib
import pkgutil

from .logging import logging


def list_plugins(cls):
    """ Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
        which is the name of a module to load. Loads that module and iterates over the namespace,
        yielding the name of modules in said namespace.
    """
    module = importlib.import_module(cls.plugin_namespace)
    logging.debug("cls '{}', namespace '{}', module '{}'".format(cls, cls.plugin_namespace, module))
    for finder, name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
        logging.debug("Found plugin '{}'".format(name))
        yield name, importlib.import_module(name)


class PluginClass(object):

    def __init__(self, **kwargs):
        logging.debug("{}.__init__({})".format(self.__class__.__name__, kwargs))
        self.__dict__.update(kwargs)
        return

    @classmethod
    def init(cls, **kwargs):
        """ Look for a plugin for this object, and return a new object of that plugin
            with its own class (that inherits this class - or should, anyway).
            Otherwise return this class's object.
        """
        logging.debug("{}.init({})".format(cls.__class__.__name__, kwargs))

        plugins = dict(list_plugins(cls))

        if 'type' in kwargs:
            for plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug(
                        "Found {} type '{}', returning object '{}'".format(
                            cls.__class__.__name__,
                            plugin_ref.type,
                            plugin_ref
                        )
                    )
                    return plugin_ref.classref(**kwargs)
            raise Exception("No such {} type '{}'".format(cls.__class__.__name__, kwargs['type']))

    @classmethod
    async def load_plugins(cls, **kwargs):
        """ If this class has a variable 'plugin_namespace', search that namespace
            for modules. If a module has the function 'plugin_init', run it, passing
            any kwargs passed to us.
        """
        logging.debug("load_plugins(): starting")

        plugins = dict(list_plugins(cls))

        for plugin_name, plugin_ref in plugins.items():
            if hasattr(plugin_ref, "plugin_init") and callable(plugin_ref.plugin_init):
                logging.debug("Loading plugin {}".format(plugin_name))
                await plugin_ref.plugin_init(**kwargs)
                logging.debug("Done loading plugin {}".format(plugin_name))
            else:
                logging.debug("No attribute 'plugin_init' in plugin {}".format(plugin_name))
