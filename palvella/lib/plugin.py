
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
            self._plugins = self.load_plugins()
        topo = self.topo_sort(self._plugins.class_graph)
        return topo

    @plugins.setter
    def set_plugins(self, value=None):
        self._plugins = value

    def topo_sort(self, graph):
        ts = graphlib.TopologicalSorter(graph)
        return tuple(ts.static_order())

    def walk_plugins(self):
        wp = WalkPlugins()
        wp.walk_subclass(self.__class__)
        return wp

    def load_plugins(self, **kwargs):
        """Discover and import all plugins, and return a WalkPlugins object.

           WalkPlugins 'class_graph' is modified to include classes that depend on other classes, without inheriting them;
           that way a class can declare a dependency on another plugin, without needing to have any code depend on it.
        """
        self._logger.debug(f"load_plugins({self}, {kwargs})")
        wp = self.walk_plugins()

        for cls in wp.classes:
            # Add graph items for classes that depend on other classes,
            # but that don't want to do multiple inheritance. To do this the
            # class can have an attribute 'depends_on', which can define
            # different properties that we will use to identify the class
            # it depends on. Once we find it, we add the dependency mapping
            # to the graph.
            if hasattr(cls, 'depends_on'):
                for dependency in cls.depends_on:
                    #self._logger.debug(f"  cls {cls} dependency {dependency}")
                    match = defaultdict(list)
                    matchclasses = wp.classes[:]
                    if 'parentclass' in dependency:
                        tmpclasses = []
                        for parentclass in [x for x in matchclasses if x.__name__ == dependency['parentclass']]:
                            #self._logger.debug(f"    parentclass {parentclass} subclasses {parentclass.__subclasses__()}")
                            #self._logger.debug(f"      graph {wp.class_graph[parentclass]}")
                            tmpclasses += wp.class_graph[parentclass]
                        matchclasses = tmpclasses
                    #self._logger.debug(f"  matchclasses {matchclasses}")
                    if 'type' in dependency:
                        tmpclasses = []
                        for m in matchclasses:
                            #self._logger.debug(f"    matchclass {m} dependency {dependency}")
                            if m.plugin_type == dependency['type']:
                                #self._logger.debug(f"    type matches")
                                tmpclasses.append(m)
                        matchclasses = tmpclasses
                    #self._logger.debug(f"  matchclasses {matchclasses}")
                    if len(matchclasses) > 0:
                        wp.class_graph[parentclass].append(cls)
        return wp


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

    def walk_subclass(self, cls):
        """Walk all modules and subclasses of a base class 'cls'.

           Store the classes found in 'self.classes'.
           Store a graph of class dependencies in 'self.class_graph'.
        """
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
