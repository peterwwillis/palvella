
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from ruamel.yaml import YAML
import importlib_resources
from pathlib import Path


from palvella.lib.plugin import Plugin

from ..logging import makeLogger


class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application."""

    plugin_namespace = "palvella.lib.instance"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if hasattr(self, 'load'):
            self.config = Config(parent=self, load=self.load)
        if self.config:
            self.initialize()

    def initialize(self):
        """Initialize the new instance."""
        self._logger.debug(f"Initializing self.__dict__ -> {self.__dict__}")
        # Load plugin subclasses from the 'Plugin' class
        self.plugins = self.load_plugins(baseclass=Plugin)
        self._config.load_components(self)

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

    plugin_namespace = "palvella.lib.instance"
    #config_namespace = "instance"
    config_data = {}
    _pre_plugins_ref_name = "__pre_plugins__"

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Arguments:
            config_data: A dict of key=value pairs loaded from Config.parse().
        """

        super().__init__(**kwargs)

        # For each module, load a 'config.yaml' file if one exists, to act as the
        # default configuration data. Configuration data passed to the object in
        # the 'config_data' attribute will overload this.
        with importlib_resources.as_file( importlib_resources.files(self.__module__).joinpath('config.yaml') ) as filename:
            if Path(filename).exists():
                with open(filename, "r", encoding="utf-8") as fd:
                    self._config_data_defaults = YAML(typ='safe').load(fd)

        if hasattr(self, '_config_data_defaults'):
            for k, v in self._config_data_defaults.items():
                if not k in self.config_data:
                    self.config_data[k] = v

        if self._pre_plugins_ref_name != None and hasattr(self, self._pre_plugins_ref_name):
            if callable(getattr(self, self._pre_plugins_ref_name)):
                getattr(self, self._pre_plugins_ref_name)()


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    parsed_components = defaultdict(list)
    parent = None
    _logger = makeLogger(__module__ + "/Config")

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            instance: A reference to the parent Instance() object that loaded this Config() object.
            load: A string which points at a YAML configuration file to load().
        """
        self._logger.debug(f"Config({kwargs})")
        self.__dict__.update(kwargs)

        if 'load' in kwargs:
            self.loadYamlFile(file=kwargs['load'])

    def loadYamlFile(self, file=None):
        """Load configuration, parse it, and return the result.

        Arguments:
            file: A YAML file with configuration data.
        """
        if file is not None:
            with open(file, "r", encoding="utf-8") as f:
                yaml = YAML(typ='safe')
                # Parse and return the config
                return self.parse(yaml.load(f))
        raise ValueError("No configuration provided")

    def parse(self, data):
        """Parse configuration data and create new objects in current instance.

        For each root key:value, look for a subclass of type 'plugin_base' that has a
        'config_namespace' attribute whose value is the same as the root key.
        Append the subclass and the value to 'self.parsed_components'.
        """

        self._logger.debug("Config.parse()")

        # We don't need to do the whole loading of plugins yet, we just need
        # to import all the modules to load all the subclasses.
        self.parent.walk_plugins()

        subclasses = self.parent.subclasses
        self._logger.debug(f"subclasses: {subclasses}")

        for datarootkey, datarootval in data.items():
            for subclass in [x for x in subclasses if x.class_type == "plugin"]:
                # The subclass must have an attribute 'config_namespace', whose value is the name
                # of the data root key.
                if not hasattr(subclass, 'config_namespace'):
                    continue
                if datarootkey == subclass.config_namespace:
                    assert (type(datarootval) is type([])), f"Configuration data entry '{datarootkey}' value must be a list"
                    for val in datarootval:
                        self.parsed_components[datarootkey].append({"class": subclass, "config_data": val})

    def load_components(self, parent):

        # NOTE: This is probably terrible design; we're explicitly excluding classes of type 'base',
        #       because we're trying to avoid loading the Instance class, because we don't want to
        #       create a new Instance while we're trying to configure the first Instance!
        #       Added an extra test to exclude the Instance class name, just to be extra explicit;
        #       this could probably use a better solution?
        base_plugins = [x for x in parent.plugins if (x.class_type == "plugin")]

        # TODO NEXT: finish writing this function so that it loads a new object for every 
        #            'objs' class, but passing in the configuration from any 'parsed_components'
        #            because those are the ones we actually want to configure.

        loaded_objects = []
        for plugin in base_plugins:
            self._logger.debug(f"plugin {plugin}")
            if hasattr(plugin, 'config_namespace') and plugin.config_namespace in self.parsed_components:
                for parsed_component in self.parsed_components[plugin.config_namespace]:
                    _class, _data = parsed_component['class'], parsed_component['config_data']
                    loaded_objects.append(_class(parent=parent, config_data=_data))
            else:
                loaded_objects.append(plugin(parent=parent))
        self._logger.debug(f"loaded_objects: {loaded_objects}")
