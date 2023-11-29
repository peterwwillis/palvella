
"""The base class for the Instance. Defines plugin class and some base functions."""

from collections import defaultdict
from ruamel.yaml import YAML

from palvella.lib.plugin import Plugin

from ..logging import makeLogger


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

    async def initialize(self):
        self._logger.debug(f"Initializing self.__dict__ -> {self.__dict__}")
        await self._config.load_components(self)

    async def configure(self, load):
        self._logger.debug(f"configure()")
        self._config = Config(parent=self, load=load)


class Config:
    """A class to parse a configuration file and load it into a data structure."""

    #plugin_namespace = None
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

        Given configuration data, examine the keys of the data and look for a subclass
        of the Instance class that matches that subclass's 'config_namespace'.

        For each array element in the value of the key, make a new object of that
        subclass, passing the data of that element.

        The end result is this Config() object has attributes whose names are that
        of a 'config_namespace', and whose value is an array of objects.
        """

        self._logger.debug("Config.parse()")

        # We don't need to do the whole loading of plugins yet, we just need
        # to import all the modules to load all the subclasses.
        self.parent.walk_plugins()

        subclasses = self.parent.subclasses
        self._logger.debug(f"subclasses: {subclasses}")

        # Loop over each of the data's root key/values; assume these are configuration namespaces.
        for datarootkey, datarootval in data.items():
            self._logger.debug(f"  datarootkey {datarootkey}, datarootval {datarootval}")

            # Loop over each of the subclasses of the parent class.
            # Only look at 'plugin_base' classes; the actual 'plugin' class will be automatically
            # loaded by the base class once we pass it the plugin_type in load_components().
            for subclass in [x for x in subclasses if x.class_type == "plugin_base"]:

                # The subclass must have an attribute 'config_namespace', whose value is the name
                # of the data root key.
                if not hasattr(subclass, 'config_namespace'):
                    continue

                if datarootkey == subclass.config_namespace:
                    # Raise exception if the root value isn't a list
                    assert (type(datarootval) is type([])), f"Configuration data entry '{datarootkey}' value must be a list"

                    for val in datarootval:
                        self._logger.debug(f"Appending subclass and data value to list self.parsed_components.{datarootkey}: ({subclass.__name__}, {val})")
                        self.parsed_components[datarootkey].append({"class": subclass, "config_data": val})

    async def load_components(self, parent):

        # NOTE: This is probably terrible design; we're explicitly excluding classes of type 'base',
        #       because we're trying to avoid loading the Instance class, because we don't want to
        #       create a new Instance while we're trying to configure the first Instance!
        #       Added an extra test to exclude the Instance class name, just to be extra explicit;
        #       this could probably use a better solution?
        objs = [x for x in parent.plugins if (x.class_type != "base" and x.__name__ != "Instance")]
        self._logger.debug(f"load_components: objs {objs}")

        # TODO NEXT: finish writing this function so that it loads a new object for every 
        #            'objs' class, but passing in the configuration from any 'parsed_components'
        #            because those are the ones we actually want to configure.

        for config_namespace, array in self.parsed_components.items():
            self._logger.debug(f"loading component config ns {config_namespace}")
            for entry in array:
                cls, data = entry['class'], entry['config_data']
                self._logger.debug(f"  class {cls}, data {data}")
