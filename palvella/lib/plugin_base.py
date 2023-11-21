
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
    logging.debug(f"list_plugins({cls})")
    if not hasattr(cls, 'plugin_namespace'):
        return
    module = importlib.import_module(cls.plugin_namespace)
    #logging.debug(f"cls '{cls}', namespace '{cls.plugin_namespace}', module '{module}'")
    for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
        logging.debug(f"Found plugin '{name}'")
        yield name, importlib.import_module(name)


class PluginClass:
    """The base class for plugins. Inherit this to make a new plugin class."""

    def __init__(self, **kwargs):
        """Given a set of key=value pairs, update the object with those as attributes."""  # noqa

        logging.debug(f"{self.__class__.__name__}.__init__({kwargs})")
        self.__dict__.update(kwargs)

    async def run_plugins(self, function=None, **kwargs):
        """
        Run a function in all plugins that are subclassed from this class.

        First looks up subclasses of the current object.

        If there are sub-subclasses which contain the function we want
        to run, a new object of that sub-subclass is created,
        the function is run, and that object is collected to be returned
        at the end of this function.

        Otherwise, looks up all plugins that are subclasses of the current class.
        For each, look up function name and call it, passing \*\*kwargs.
        """
        logging.debug(f"run_plugins({self}, {kwargs})")

        components = []
        for subclass in self.__class__.__subclasses__():
            plugins = dict(list_plugins(subclass))

            donesubclass=0
            for subsubclass in subclass.__subclasses__():
                if hasattr(subsubclass, function):
                    logging.debug(f"Creating and calling {subsubclass}().{function}(instance=self, {kwargs})")
                    newobj = subsubclass(instance=self, **kwargs)
                    f_ref = getattr(newobj, function)
                    await f_ref()
                    components.append(newobj)
                    donesubclass = 1

            if donesubclass == 1: continue

            for plugin_name, plugin_ref in plugins.items():

                if hasattr(plugin_ref, function) and callable(getattr(plugin_ref, function)):
                    f_ref = getattr(plugin_ref, function)
                    logging.debug(f"Calling {plugin_name}.{function}({kwargs})")
                    component = await f_ref(**kwargs)
                    if component is not None: components.append(component)

        return components
