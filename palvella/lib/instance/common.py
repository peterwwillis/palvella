
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from ruamel.yaml import YAML
import importlib_resources
from pathlib import Path
from dataclasses import dataclass


from palvella.lib.plugin import Plugin, match_class_dependencies

from ..logging import makeLogger


class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application."""

    plugin_namespace = "palvella.lib.instance"
    components = []  # The list of instantiated objects of each plugin

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load plugin subclasses from the 'Component' class
        self.walk_plugins_args = { 'baseclass': Component }

        if hasattr(self, 'config_path'):
            self.config = Config(parent=self, config_path=self.config_path)
        if self.config:
            self.initialize()

    def initialize(self):
        """Initialize the new instance."""
        self._logger.debug(f"Initializing self.__dict__ -> {self.__dict__}")
        self.instantiate_components()

    def instantiate_components(self):
        """Create new instances of plugin objects.

           Walks the graph of all plugins of class_type 'plugin', sorted topologically 
           (to handle dependencies first).

           If there's a 'self.config.data_objects' entry for a given plugin, uses those
           'data_objects' configuration to create a new instance of that plugin.
           If no entry in 'data_objects', just creates a new instance of that plugin with
           no configuration.

           All new objects are appended to 'self.components' immediately.
        """
        base_plugins = [x for x in self.plugins.topo_sort() if (x.class_type == "plugin")]
        for plugin in base_plugins:
            data_objects = [x for x in self.config.data_objects if x.config_namespace == plugin.config_namespace]
            if len(data_objects) > 0:
                for obj in data_objects:
                    self.components.append(obj.classref(parent=self, config_data=obj.config_data))
            else: # Create a new object with no configuration data
                self.components.append(plugin(parent=self))

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, arg):
        self._config = arg


class Component(Plugin, class_type="base"):
    """A class to create Instance Components from.

    If an object inheriting this class has a function '__pre_plugins__',
    that function will be run at the end of '__init__' in this object.

    Attributes:
        plugin_namespace: The namespace for this plugin module.
        config_namespace: The namespace for configuration files relevant to this plugin.
        _config:           A new Config() object created by configure().
    """

    # The name of 'Component's plugin namespace. Each component needs to overload this.
    # TODO: maybe move this to the outer file itself and not in the classes?
    plugin_namespace = "palvella.lib.instance"
    #config_namespace = "instance"
    config_data = {}  # Each component gets an empty config_data by default
    _pre_plugins_ref_name = "__pre_plugins__"

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Arguments:
            parent: A reference to the parent Instance() object
            config_data: A dict of key=value pairs loaded from Config.parse().
        """
        super().__init__(**kwargs)

        # For each module, load a 'config.yaml' file if one exists, to fill in
        # default configuration data. Configuration data passed to the object in
        # the 'config_data' attribute will overload this.
        config_yaml_file = importlib_resources.files(self.__module__).joinpath('config.yaml')
        with importlib_resources.as_file(config_yaml_file) as filename:
            if Path(filename).exists():
                with open(filename, "r", encoding="utf-8") as fd:
                    self._config_data_defaults = YAML(typ='safe').load(fd)

        if hasattr(self, '_config_data_defaults'):
            for k, v in self._config_data_defaults.items():
                if not k in self.config_data:
                    self.config_data[k] = v

        # Run the '_pre_plugins_ref_name' function if it was defined by a subclass
        if self._pre_plugins_ref_name != None and hasattr(self, self._pre_plugins_ref_name):
            if callable(getattr(self, self._pre_plugins_ref_name)):
                getattr(self, self._pre_plugins_ref_name)()

    def get_component(self, dep):
        self._logger.debug(f"get_component({self}, {dep})")
        self._logger.debug(f"self.parent.plugins {self.parent.plugins}")
        objects = self.parent.components
        self._logger.debug(f"objects: {objects}")
        results = match_class_dependencies(self, objects, [dep])
        self._logger.debug(f"results: {results}")
        return results


@dataclass(unsafe_hash=True)
class ConfigDataObject:
    config_namespace = None
    classref = None
    config_data = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    _logger = makeLogger(__module__ + "/Config")
    _config_path = None

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            parent: A reference to the parent Instance() object
            load: A string which points at a YAML configuration file to load().
        """
        self._logger.debug(f"Config({kwargs})")
        self.__dict__.update(kwargs)
        self.load_config()

    def load_config(self, config_path=None):
        config_path = self.config_path if self.config_path else config_path
        if config_path:
            self.loadYamlFile(file=self.config_path)
            self.data_objects = self.get_data_objects()

    def loadYamlFile(self, file):
        """Load configuration, parse it, and return the result."""
        with open(file, "r", encoding="utf-8") as f:
            yaml = YAML(typ='safe')
            self.data = yaml.load(f)
            return
        raise ValueError("No configuration provided")

    def get_data_objects(self):
        """
        Parse configuration data. Return a dict consisting of ConfigDataObject() instances.

        For each key:value (in the root of 'self.data'), look for a subclass of type 'plugin_base'
        that has a 'config_namespace' attribute whose value is the same as the root key.
        Create an object of that and return a list of them.
        """
        objects = []

        # Load plugins to get subclasses
        self.parent.plugins
        subclasses = self.parent.subclasses

        for datarootkey, datarootval in self.data.items():
            for subclass in [x for x in subclasses if x.class_type == "plugin"]:
                if not hasattr(subclass, 'config_namespace'):
                    continue
                if datarootkey != subclass.config_namespace:
                    continue
                assert (type(datarootval) is type([])), f"Configuration data entry '{datarootkey}' value must be a list"
                for val in datarootval:
                    objects.append( ConfigDataObject(
                        config_namespace=datarootkey,
                        classref=subclass,
                        config_data=val
                    )
                )

        return objects

