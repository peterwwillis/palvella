
"""A module that defines a base class for plugins."""

import importlib
import pkgutil

from .logging import logging


def list_plugins(cls):
    """
    Generate a list of plugin names and namespaces.

    Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
    which is the name of a module to load. Loads that module and iterates over the namespace,
    yielding the name of modules in said namespace.
    """

    module = importlib.import_module(cls.plugin_namespace)
    logging.debug(f"cls '{cls}', namespace '{cls.plugin_namespace}', module '{module}'")
    for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
        logging.debug(f"Found plugin '{name}'")
        yield name, importlib.import_module(name)


class PluginClass:
    """The base class for plugins. Inherit this to make a new plugin class."""

    def __init__(self, **kwargs):
        """The __init__ method. Given a set of key=value pairs, update the object with those as attributes."""  # noqa

        logging.debug(f"{self.__class__.__name__}.__init__({kwargs})")
        self.__dict__.update(kwargs)

    @classmethod
    def init(cls, **kwargs):
        """Initialize a new object for a plugin of a given type and return it."""

        logging.debug(f"{cls.__class__.__name__}.init({kwargs})")
        plugins = dict(list_plugins(cls))

        if 'type' in kwargs:
            for _plugin_name, plugin_ref in plugins.items():
                if kwargs['type'] == plugin_ref.type:
                    logging.debug(
                        "Found {} type '{}', returning object '{}'".format(  # noqa
                            cls.__class__.__name__,
                            plugin_ref.type,
                            plugin_ref
                        )
                    )
                    return plugin_ref.ClassRef(**kwargs)
            raise ValueError(f"No such {cls.__class__.__name__} type '{kwargs['type']}'")
        raise ValueError("No 'type' argument passed")

    @classmethod
    async def load_plugins(cls, **kwargs):
        """
        Run a function in a plugin after all plugins have been imported.

        If the plugin's class has a variable 'plugin_namespace', search that namespace
        for modules. If one of those modules has the function 'plugin_init', run it, passing
        any kwargs passed to us.
        """
        logging.debug("load_plugins(): starting")

        plugins = dict(list_plugins(cls))

        for plugin_name, plugin_ref in plugins.items():
            if hasattr(plugin_ref, "plugin_init") and callable(plugin_ref.plugin_init):
                logging.debug(f"Loading plugin {plugin_name}")
                await plugin_ref.plugin_init(**kwargs)
                logging.debug(f"Done loading plugin {plugin_name}")
            else:
                logging.debug(f"No attribute 'plugin_init' in plugin {plugin_name}")
