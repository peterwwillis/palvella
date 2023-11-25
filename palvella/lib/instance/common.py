
"""The base class for the Instance. Defines plugin class and some base functions."""

from ruamel.yaml import YAML

from palvella.lib.plugin_base import PluginClass

from ..logging import logging


class Instance(PluginClass):
    """The 'Instance' plugin class. Creates a new instance of the application.

    Attributes:
        plugin_namespace: The namespace for this plugin module.
        _config:           A new Config() object created by __init__.
    """

    #plugin_namespace = "palvella.plugins.lib.instance"

    config_data_defaults = None
    config_data = {}

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Arguments:
            config: The name of a YAML configuration to load and parse. Created object becomes '_config' attribute.

        """
        super().__init__(**kwargs)

        """
        If 'config_data' was set (from Config.parse) and 'config_data_defaults' was set (in the
        class that's inheriting this class), look in the attributes of the inheriting class for
        a default attribute of the same name, and fill in 'config_data' with its value.
        """
        if hasattr(self, 'config_data_defaults') and self.config_data_defaults is not None:
            for k in self.config_data_defaults:
                if not k in self.config_data:
                    self.config_data[k] = getattr(self, k)

        # Other classes will inherit this function, but we don't want this logic
        # happening anywhere else.
        if self.__class__.__name__ == "Instance":
            if 'config' in kwargs:
                self._config = Config(instance=self, load=kwargs['config'])

    async def initialize(self):
        self._instance = self
        logging.debug(f"self.__dict__ -> {self.__dict__}")
        self.components = await self.run_plugin_function(function="instance_init")


class Config(Instance):
    """The class that configures an instance."""

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            instance: A reference to the parent Instance() object that loaded this Config() object.
            load: A string which points at a YAML configuration file to load().
        """
        logging.debug(f"Config({kwargs})")
        self.__dict__.update(kwargs)

        assert ('instance' in kwargs), f"new Config() object must have instance attribute passed to it"
        assert (kwargs['instance'].__class__.__name__ == "Instance"), f"new Config() object's instance attribute must be of type Instance"

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

        Given configuration data, examine the keys of the data and look for a subclass
        of the Instance class that matches that subclass's 'config_namespace'.

        For each array element in the value of the key, make a new object of that
        subclass, passing the data of that element.

        The end result is this Config() object has attributes whose names are that
        of a 'config_namespace', and whose value is an array of objects.
        """

        logging.debug("Config.parse()")
        # Instance objects are subclasses of 'Instance' class.
        subclasses = [cls for cls in Instance.__subclasses__()]
        for rootkey, rootval in data.items():
            for subclass in subclasses:
                # The subclass must have an attribute 'config_namespace', whose value is the name
                # we look for to create a new object for that subclass.
                if not hasattr(subclass, 'config_namespace'):
                    continue
                if rootkey == subclass.config_namespace:
                    assert (type(rootval) is type([])), f"Configuration data entry '{rootkey}' value must be a list"
                    if not rootkey in self.__dict__:
                        self.__dict__[rootkey] = []
                    for val in rootval:
                        logging.debug(f"Appending new object to self.[{rootkey}]: {subclass.__name__}(instance=self.instance, {val})")
                        self.__dict__[rootkey].append(subclass(instance=self.instance, config_data=val))
