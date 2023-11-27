
"""The base class for the Instance. Defines plugin class and some base functions."""

from ruamel.yaml import YAML

from palvella.lib.plugin import Plugin

from ..logging import logging


class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application.

    Attributes:
        plugin_namespace: The namespace for this plugin module.
        _config:           A new Config() object created by configure().
    """

    plugin_namespace = "palvella.lib.instance"
    #config_namespace = "instance"

    config_data_defaults = None
    config_data = {}
    _pre_plugins_ref_name = "__pre_plugins__"

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Arguments:
            config_data: A dict of key=value pairs loaded from Config.parse().
            config_data_defaults: A dict of default values to fill in config_data with.
        """

        super().__init__(**kwargs)

        if hasattr(self, 'config_data_defaults') and self.config_data_defaults is not None:
            for k, v in self.config_data_defaults.items():
                if not k in self.config_data:
                    self.config_data[k] = v

        # Run a function *before* loading the plugins below. This allows inheriting classes to initialize
        # the object prior to loading more child plugins, so the child plugins can use the initialized
        # object.
        if self._pre_plugins_ref_name != None and hasattr(self, self._pre_plugins_ref_name):
            if callable(getattr(self, self._pre_plugins_ref_name)):
                getattr(self, self._pre_plugins_ref_name)()

        logging.debug("running self.load_plugins")
        self.load_plugins(create_objs=False)

    async def initialize(self):
        logging.debug(f"Instance: self.__dict__ -> {self.__dict__}")
        await self._config.load_components(self)

    async def configure(self, load):
        self._config = Config(load=load)


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    plugin_namespace = None
    components = {}

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            instance: A reference to the parent Instance() object that loaded this Config() object.
            load: A string which points at a YAML configuration file to load().
        """
        logging.debug(f"Config({kwargs})")
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
        logging.debug(f"subclasses: {subclasses}")

        # Loop over each of the data object's root key/values
        for datarootkey, datarootval in data.items():

            # Loop over each of the subclasses of the 'Instance' class
            for subclass in subclasses:

                # The subclass must have an attribute 'config_namespace', whose value is the name
                # of the data root key.
                if not hasattr(subclass, 'config_namespace'):
                    continue

                # Data root key matches 'config_namespace'
                if datarootkey == subclass.config_namespace:
                    # Raise exception if the root value isn't a list
                    assert (type(datarootval) is type([])), f"Configuration data entry '{datarootkey}' value must be a list"

                    if not datarootkey in self.components:
                        self.components[datarootkey] = []

                    for val in datarootval:
                        logging.debug(f"Appending subclass and data value to list self.components.{datarootkey}: ({subclass.__name__}, {val})")
                        self.components[datarootkey].append({"class": subclass, "config_data": val})

    async def load_components(self, parent):
        objs = parent.load_plugins()
        logging.debug(f"objs: {objs}")

        for name, array in self.components.items():
            logging.debug(f"loading component {name}")
            for d in array:
                cls, data = d['class'], d['config_data']
                logging.debug(f"class {cls} data {data}")
                objs = parent.load_plugins()
                logging.debug(f"objs: {objs}")
