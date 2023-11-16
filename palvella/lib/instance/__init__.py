
"""The library for instances. Defines plugin class and some base functions."""

from ruamel.yaml import YAML

from ..logging import logging
from palvella.lib.plugin_base import PluginClass


class Instance(PluginClass):
    """The 'Instance' plugin class. Creates a new instance of the application.

    Attributes:
        plugin_namespace: The namespace for this plugin module.
        config:           A new Config() object created by __init__.
    """

    #plugin_namespace = "palvella.plugins.lib.instance"

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Accepts arbitrary key=value pairs which are filled into the object attributes.
        Then creates an attribute 'config' with a new Config() object.
        """
        super().__init__(**kwargs)
        if 'config' in kwargs:
            self._config = Config(load=kwargs['config'])


class Component(PluginClass):
    """A class for instance components to inherit."""
    pass


class Config(Instance):
    """The class that configures an instance."""

    def __init__(self, **kwargs):
        """Initialize new configuration.

        Arguments:
            load: A string which points at a YAML configuration file to load().
        """
        #super().__init__(**kwargs)
        logging.debug(f"Config({kwargs})")
        if 'load' in kwargs:
            self.load(file=kwargs['load'])

    def load(self, file=None):
        """Load configuration, parse it, and return the result.

        Arguments:
            file: A YAML file with configuration data.
        """
        if file is not None:
            with open(file, "r", encoding="utf-8") as f:
                yaml = YAML(typ='safe')
                return self.parse(yaml.load(f))
        raise ValueError("No configuration provided")

    def parse(self, data):
        """Parse configuration data and create new objects in current instance.

        Given configuration data, examine the keys of the data and look for a subclass
        of the Component class that matches that subclass's 'config_namespace'.

        For each array element in the value of the key, make a new object of that
        subclass, passing the data of that element.

        The end result is this Config() object has attributes whose names are that
        of a 'config_namespace', and whose value is an array of objects.
        """

        # Component objects are subclasses of 'Component' class.
        subclasses = [cls for cls in Component.__subclasses__()]
        for rootkey, rootval in data.items():
            for subclass in subclasses:
                if rootkey == subclass.config_namespace:
                    assert (type(rootval) is type([])), f"Configuration data entry '{rootkey}' value must be a list"
                    if not rootkey in self.__dict__:
                        self.__dict__[rootkey] = []
                    for val in rootval:
                        self.__dict__[rootkey].append(subclass(**val))


import palvella.lib.instance.action
import palvella.lib.instance.db
import palvella.lib.instance.engine
import palvella.lib.instance.frontend
import palvella.lib.instance.job
import palvella.lib.instance.trigger
