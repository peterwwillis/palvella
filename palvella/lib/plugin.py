
"""A module that defines a base class for plugins."""

import importlib
import pkgutil
from collections import defaultdict
from dataclasses import dataclass

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
    plugin_namespace = None
    component_namespace = None

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

    def load_plugins(self, **kwargs):
        """Discover and import all plugins, and return a WalkPlugins object."""
        #self._logger.debug(f"load_plugins({self}, {kwargs})")
        wp = self.walk_plugins(**kwargs)
        return wp

    def walk_plugins(self, args=None):
        # TODO: FIXME: currently if this is run from Instance(), it will result in duplicate
        # entries in wp.classes. Fix this?
        if hasattr(self, 'walk_plugins_args'):
            args = self.walk_plugins_args
        if not 'baseclass' in args:
            args['baseclass'] = self.__class__
        wp = WalkPlugins()
        #self._logger.debug(f"  walk_plugins({self}, {args})")
        wp.walk_subclass(args['baseclass'])
        wp.add_graph_dependencies()
        return wp

    @property
    def plugins(self):
        if self._plugins == None:
            self.plugins = self.load_plugins()
        return self._plugins
    @plugins.setter
    def plugins(self, value=None):
        self._plugins = value



class PluginDependency:
    """A class to declare what dependency (on another class/plugin) a plugin has.

       Attributes:
            parentclass:    The name of a class which should be the parent class of the class we want to find.
            plugin_type:    The 'plugin_type' attribute of the class we want to find.
    """
    parentclass = None
    plugin_type = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_class(obj):
    if isinstance(obj, type):
        return obj
    return obj.__class__

def match_class_dependencies(self, objects, deps):
    """Match a class or instance of a class against a PluginDependency().

       'self' is just any object with a '_logger' method.
       'objects' is a list of either classes or class instances.
       'deps' is a list of PluginDepency() instances.

       Returns the matching classes/instances.
    """
    def matchParentClass(self, objects, dep):
            for match in objects:
                #self._logger.debug(f"  match {match}")
                for parent in get_class(match).__bases__:
                    if dep.parentclass == parent.__name__:
                        #self._logger.debug(f"Found parent class {parent} in class of object {match}]")
                        yield match
    def matchPluginType(self, objects, dep):
            for obj in [x for x in objects if x.plugin_type == dep.plugin_type]:
                #self._logger.debug(f"Found plugin_type {dep.plugin_type} for object {obj}")
                yield obj
    results = []
    for dep in deps:
        #self._logger.debug(f"dep {dep}")
        matches = objects[:]
        #self._logger.debug(f"matches: {matches}")
        if dep.parentclass != None:
            matches = matchParentClass(self, matches, dep)
        if dep.plugin_type != None:
            matches = matchPluginType(self, matches, dep)
        results += matches
    #self._logger.debug(f"found deps: {results}")
    return results

@dataclass(unsafe_hash=True)
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

    def topo_sort(self, graph=None):
        if graph == None:
            graph = self.class_graph
        ts = graphlib.TopologicalSorter(graph)
        return tuple(ts.static_order())

    def get_class_dependencies(self, deps):
        results = []
        #self._logger.debug(f"get_class_dependencies({self}, {deps})")
        #self._logger.debug(f"graph {self.class_graph}")
        return match_class_dependencies(self, self.classes, deps)

    def add_graph_dependencies(self):
        """Locate classes based on some dependency meta-criteria and add the dependency to 'self.class_graph'.

        """
        for cls in self.classes:
            classes = self.get_class_dependencies(cls.depends_on)
            for _class in classes:
                if not _class in self.class_graph[cls]:
                    self.class_graph[cls].append(_class)

    def walk_subclass(self, cls):
        """Walk all modules and subclasses of class 'cls'.

           Store the classes found in 'self.classes'.
           Store a graph of class dependencies in 'self.class_graph'.
        """
        #self._logger.debug(f"  walk_subclass(self, {cls})")
        self.load_plugin_modules(cls)
        self.classes += [cls]
        #self._logger.debug(f"  appended to self.classes {self.classes}")
        subclasses = cls.__subclasses__()
        if len(subclasses) > 0:
            for x in subclasses:
                # Add class dependencies to the graph
                if not cls in self.class_graph[x]:
                    self.class_graph[x].append(cls)
            for subclass in subclasses:
                self.walk_subclass(subclass)

    def load_plugin_modules(self, cls):
        """Run self.list_class_plugins and return only the import_module() results."""
        return list(v for k,v in [x for x in self.list_class_plugins(cls) if x is not None])

    def list_class_plugins(self, cls):
        """Generate a list of plugin names and namespaces.

        Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
        which is the name of a module to load. Loads that module and iterates over the namespace,
        yielding the name of modules in said namespace.
        """
        #self._logger.debug(f"      list_class_plugins({cls})")
        if not hasattr(cls, 'plugin_namespace') or cls.plugin_namespace == None:
            self._logger.debug(f"        No 'plugin_namespace' found in class {cls}")
            yield
        else:
            if cls.plugin_namespace in self.searched_module_ns:
                yield
            else:
                module = importlib.import_module(cls.plugin_namespace)
                for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    #self._logger.debug(f"        Class {cls}: Found plugin '{name}'")
                    yield name, importlib.import_module(name)
                self.searched_module_ns.append(cls.plugin_namespace)