
"""A module that defines a base class for plugins."""

import importlib
import pkgutil

from .logging import logging


def list_class_plugins(cls):
    """
    Generate a list of plugin names and namespaces.

    Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
    which is the name of a module to load. Loads that module and iterates over the namespace,
    yielding the name of modules in said namespace.
    """
    logging.debug(f"list_class_plugins({cls})")
    if not hasattr(cls, 'plugin_namespace') or cls.plugin_namespace == None:
        logging.debug(f"No 'plugin_namespace' found in class {cls}")
        yield
    else:
        module = importlib.import_module(cls.plugin_namespace)
        for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
            logging.debug(f"Class {cls}: Found plugin '{name}'")
            yield name, importlib.import_module(name)


class Plugin:
    """The base class for plugins. Inherit this to make a new plugin class."""

    def __init__(self, **kwargs):
        """Given a set of key=value pairs, update the object with those as attributes."""  # noqa

        logging.debug(f"{self.__class__.__name__}.__init__({kwargs})")
        self.__dict__.update(kwargs)

    def load_plugins(self, function=None, subsubclasses=True, modules=True, create_objs=True, **kwargs):
        """
        Based on the current class, load plugins and run an optional function, returning results.

        First looks up subclasses of the current object.

        If there are sub-subclasses which contain the function we want
        to run, a new object of that sub-subclass is created,
        the function is run, and that object is collected to be returned
        at the end of this function.

        Otherwise, looks up all plugins that are subclasses of the current class.
        For each, look up function name and call it, passing \*\*kwargs.

        Arguments:
            If subsubclasses is True, looks at all sub-subclasses of the current class, iterating
            over them. If 'function' attribute is not None, looks for that function in each
            sub-subclass, and calls it, returning the result.

            If modules is True, looks at 'plugin_namespace' attribute of the current class, and loads
            any modules found in that namespace.

            If create_objs is True, attempts to create a new object for each plugin class found,
            and returns the list. If create_objs is False, returns an empty list.
        """

        def get_ref(refs, function):
            """Pass a list of references and optional function reference, get back a callable or nothing."""
            for ref in refs:
                if function != None and hasattr(ref, function) and callable(getattr(ref, function)):
                    yield getattr(ref, function)
                elif callable(ref):
                    yield ref
                yield

        logging.debug(f"load_plugins({self}, function=\"{function}\", {kwargs})")
        objs = []

        # Run this before anything else. It will load the plugin namespace of the current class
        # and discover and import all the modules. That will load in new subclasses of the
        # current class, allowing us to find more plugins to load.
        class_plugins = list(v for k,v in [x for x in list_class_plugins(self.__class__) if x is not None])

        logging.debug(f"subclasses: {self.__class__.__subclasses__()}")
        for subclass in self.__class__.__subclasses__():

            plugin_refs = list(v for k,v in [x for x in list_class_plugins(subclass) if x is not None])

            if subsubclasses:
                for ref in [x for x in get_ref(subclass.__subclasses__(), function) if x is not None]:
                    if create_objs:
                        logging.debug(f"adding obj: {ref}(parent=self, {kwargs})")
                        objs.append(ref(parent=self, **kwargs))

            if modules:
                for ref in [x for x in get_ref(plugin_refs, function) if x is not None]:
                    if create_objs:
                        logging.debug(f"adding module: {ref}({kwargs})")
                        objs.append(ref(**kwargs))

        logging.debug(f"subclasses: {self.__class__.__subclasses__()}")

        return objs
