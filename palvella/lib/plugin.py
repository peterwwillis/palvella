
"""A module that defines a base class for plugins."""

import importlib
import pkgutil
from functools import lru_cache
from collections import defaultdict
from dataclasses import dataclass

import graphlib  # our poetry requirements include the 'graphlib_backport' module

from .logging import makeLogger


_logger = makeLogger(__name__)


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


class PluginDependency:
    """A class to declare what dependency (on another class/plugin) a plugin has.

       Attributes:
            classname:              The name of a class we want to find.
            parentclassname:        The name of a parent of the class we want to find.
            plugin_type:            The 'plugin_type' attribute of the class we want to find.
            component_namespace:    The 'component_namespace' attribute of the class we want to find.
    """
    classname = None
    parentclassname = None
    plugin_type = None
    component_namespace = None
    def __init__(self, **kwargs):
        for k in ("classname", "parentclassname", "plugin_type","component_namespace"):
            if k in kwargs:
                if type(kwargs[k]) != type(""):
                    raise Exception("Error: type(%s) must be type %s" % (k, type("")) )
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


def get_class(obj):
    """Return the class reference for either an instance of a class, or just the class reference"""
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
    _logger.debug(f"objects {objects}")
    # Wrap the list arguments with tuples so that it's hashable for @lru_cache
    return match_class_dependencies_wrapper(self, tuple(objects), tuple(deps))
@lru_cache
def match_class_dependencies_wrapper(self, objects, deps):
    """Implementation of match_class_dependencies()"""
    def matchParentClass(self, objects, dep):
        for match in objects:
            for parent in get_class(match).__bases__:
                if dep.parentclassname == parent.__name__:
                    yield match
    def matchClass(self, objects, dep):
        for obj in [x for x in objects if x.__name__ == dep.classname]:
            yield obj
    def matchPluginType(self, objects, dep):
        for obj in [x for x in objects if x.plugin_type == dep.plugin_type]:
            yield obj
    def matchComponentNs(self, objects, dep):
        for obj in [x for x in objects if x.component_namespace == dep.component_namespace]:
            yield obj
    results = []
    for dep in deps:
        matches = objects[:]
        if dep.classname != None:
            matches = matchClass(self, matches, dep)
        if dep.parentclassname != None:
            matches = matchParentClass(self, matches, dep)
        if dep.plugin_type != None:
            matches = matchPluginType(self, matches, dep)
        if dep.component_namespace != None:
            matches = matchComponentNs(self, matches, dep)
        results += matches
    return results

@dataclass(unsafe_hash=True)
class WalkPlugins:
    """
    Manage the traversal of plugins and their classes.

    Arguments:
        baseclass:      A class to walk subclasses of and build a plugin graph of.

    Attributes:
        classes:        A list of classes discovered
        class_graph:    A graph of classes and the subclasses dependent on them
    """

    _logger = makeLogger(__module__ + "/WalkPlugins")

    # The graph of class dependencies as they are discovered
    # (subclass Y depends on subclass X, etc)
    class_graph = defaultdict(list)

    # A flat list of classes as they are discovered
    classes = []

    # A list of plugin namespaces that have already been searched for modules to
    # import, so we don't go over them again and again unnecessarily.
    searched_module_ns = []

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    @lru_cache
    def __init__(self, baseclass):
        self.walk_subclass(baseclass)
        self.add_graph_dependencies()

    def topo_sort(self, graph=None):
        """Return a topologically sorted tuple of the graph of classes."""
        if graph == None:
            graph = self.class_graph
        ts = graphlib.TopologicalSorter(graph)
        return tuple(ts.static_order())

    def add_graph_dependencies(self):
        """Locate classes based on some dependency meta-criteria and add the dependency to 'self.class_graph'."""
        for cls in self.classes:
            if len(cls.depends_on) < 1:
                continue
            for _class in match_class_dependencies(self, self.classes, cls.depends_on):
                if not _class in self.class_graph[cls]:
                    self.class_graph[cls].append(_class)

    def walk_subclass(self, cls):
        """
        Walk all modules and subclasses of class 'cls'.

        Stores the classes found in 'self.classes'.
        Stores a graph of class dependencies in 'self.class_graph'.
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
        """Run self.load_class_plugins and return only the import_module() results."""
        return list(v for k,v in [x for x in self.load_class_plugins(cls) if x is not None])

    def load_class_plugins(self, cls):
        """
        Generate a list of plugin names and namespaces.

        Accepts a class, which needs an attribute 'plugin_namespace', whose value is a string
        which is the name of a module to load. Loads that module and iterates over the namespace,
        yielding the name of modules in said namespace.
        """
        if not hasattr(cls, 'plugin_namespace') or cls.plugin_namespace == None:
            self._logger.debug(f"        No 'plugin_namespace' found in class {cls}")
            yield
        else:
            if cls.plugin_namespace in self.searched_module_ns:
                yield
            else:
                module = importlib.import_module(cls.plugin_namespace)
                for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + "."):
                    yield name, importlib.import_module(name)
                self.searched_module_ns.append(cls.plugin_namespace)
