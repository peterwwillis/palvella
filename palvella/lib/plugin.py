
"""A module that defines a base class for plugins."""

import importlib
import pkgutil
from collections import defaultdict

import graphlib  # our poetry requirements include the 'graphlib_backport' module

from .logging import makeLogger


class Plugin:
    """The base class for plugins. Inherit this to make a new plugin class."""
    subclasses = []  # A list of all subclasses of this class
    _logger = None  # makeLogger(__name__)
    _plugins = None
    # Should be a list of PluginDependency objects
    depends_on = []
    class_type = None

    def __init__(self, **kwargs):
        """Given a set of key=value pairs, update the object with those as attributes."""  # noqa
        self._logger = makeLogger(self.__class__.__module__ + "/" + self.__class__.__name__)
        self._logger.debug(f"{self.__class__.__name__}.__init__({kwargs})")
        self.__dict__.update(kwargs)

    def __init_subclass__(cls, class_type=None, plugin_type=None, **kwargs):
        """Allow the parent class to track subclasses, and specify a type for the subclass."""
        cls.class_type = class_type
        cls.plugin_type = plugin_type
        super().__init_subclass__(**kwargs)
        cls.subclasses.append(cls)

    @property
    def plugins(self):
        if self._plugins == None:
            self.plugins = self.load_plugins()
        topo = self.topo_sort(self._plugins.class_graph)
        return topo
    @plugins.setter
    def plugins(self, value=None):
        self._plugins = value

    def topo_sort(self, graph):
        ts = graphlib.TopologicalSorter(graph)
        return tuple(ts.static_order())

    def walk_plugins(self, baseclass=None):
        if baseclass == None:
            baseclass = self.__class__
        wp = WalkPlugins()
        self._logger.debug(f"  walk_plugins({self}, {baseclass})")
        wp.walk_subclass(baseclass)
        wp.add_graph_dependencies()
        return wp

    def load_plugins(self, **kwargs):
        """Discover and import all plugins, and return a WalkPlugins object."""
        self._logger.debug(f"load_plugins({self}, {kwargs})")
        wp = self.walk_plugins(**kwargs)
        return wp


class PluginDependency:
    """A class to declare what dependency (on another class/plugin) a plugin has."""
    parentclass = None
    plugin_type = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class WalkPlugins:
    """Manage the traversal of plugins and their classes."""

    _logger = makeLogger(__module__ + "/WalkPlugins")

    # The graph of class dependencies as they are discovered
    # (subclass Y depends on subclass X, etc)
    class_graph = defaultdict(list)

    # A flat list of classes as they are discovered
    classes = []

    # A list of plugin namespaces that have already been searched for modules to
    # import, so we don't go over them again and again unnecessarily.
    searched_module_ns = []


    def get_class_dependencies(self, deps):
        results = []
        for dep in deps:
            matchclasses = self.classes[:]
            if dep.parentclass != None:
                tmpclasses = []
                for parentclass in [x for x in matchclasses if x.__name__ == dep.parentclass]:
                    tmpclasses += self.class_graph[parentclass]
                matchclasses = tmpclasses
            if dep.plugin_type != None:
                tmpclasses = []
                for cls in [x for x in matchclasses if x.plugin_type == dep.plugin_type]:
                    tmpclasses.append(cls)
                matchclasses = tmpclasses
            results += matchclasses
        return results

    def add_graph_dependencies(self):
        """Locate classes based on some dependency meta-criteria and add the dependency to 'self.class_graph'.

           Dependency attributes:
                parentclass:    The name of a class which should be the parent class of the class we want to find.
                plugin_type:    The 'plugin_type' attribute of the class we want to find.
        """
        for cls in self.classes:
            classes = self.get_class_dependencies(cls.depends_on)
            for _class in classes:
                self.class_graph[_class].append(cls)

    def walk_subclass(self, cls):
        """Walk all modules and subclasses of a base class 'cls'.

           Store the classes found in 'self.classes'.
           Store a graph of class dependencies in 'self.class_graph'.
        """
        self._logger.debug(f"  walk_subclass(self, {cls})")
        self.load_plugin_modules(cls)
        self.classes += [cls]
        subclasses = cls.__subclasses__()
        if len(subclasses) > 0:
            for x in subclasses:
                # Add class dependencies to the graph
                self.class_graph[x].append(cls)
            for subclass in subclasses:
                self.walk_subclass(subclass)

    def load_plugin_modules(self, cls):
        """Run self.list_class_plugins and return only the import_module() results."""
        return list(v for k,v in [x for x in self.list_class_plugins(cls) if x is not None])

    def list_class_plugins(self, cls):
        """
        Generate a list of plugin names and namespaces.

        Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
        which is the name of a module to load. Loads that module and iterates over the namespace,
        yielding the name of modules in said namespace.
        """
        self._logger.debug(f"      list_class_plugins({cls})")
        if not hasattr(cls, 'plugin_namespace') or cls.plugin_namespace == None:
            self._logger.debug(f"        No 'plugin_namespace' found in class {cls}")
            yield
        else:
            if cls.plugin_namespace in self.searched_module_ns:
                yield
            else:
                module = importlib.import_module(cls.plugin_namespace)
                for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    self._logger.debug(f"        Class {cls}: Found plugin '{name}'")
                    yield name, importlib.import_module(name)
                self.searched_module_ns.append(cls.plugin_namespace)
