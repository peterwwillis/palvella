
"""The library for instances. Defines plugin class and some base functions."""

from ruamel.yaml import YAML

from palvella.lib.plugin_base import PluginClass

from .db import DB
from .engine import Engine
from .job import Job
from .logging import logging
from .trigger import Trigger


class Config:
    """The class that configures an instance."""

    dbs = []
    engines = []
    jobs = []
    triggers = []

    def __init__(self, **kwargs):
        """Initialize new object."""
        logging.debug(f"Config.__init__({kwargs})")
        self.__dict__.update(kwargs)

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

        Parses a dict for a set of keys. If a matching object is found for
        a given key, a new object is created and the value for that key is
        passed to its 'init' function. The new object is appended to an array
        in the current object. This is not idempotent; only run this once
        per Config object.
        """

        if 'db' in data:
            assert (data['db'] is list), "'db' value must be a list"
            for db in data['db']:
                self.dbs.append(DB.init(**db))

        if 'engine' in data:
            assert (data['engine'] is list), "'engine' value must be a list"
            for engine in data['engine']:
                self.engines.append(Engine.init(**engine))

        if 'jobs' in data:
            assert (data['jobs'] is list), "'jobs' value must be a list"
            for job in data['jobs']:
                self.jobs.append(Job.init(**job))

        if 'triggers' in data:
            assert (data['jobs'] is list), "'jobs' value must be a list"
            for trigger in data['triggers']:
                self.triggers.append(Trigger.init(**trigger))


class Instance(PluginClass):
    """The 'Instance' plugin class.

    Attributes:
        plugin_namespace: The namespace for this plugin module.
        config:           A new Config() object created by __init__.
    """

    plugin_namespace = "palvella.plugins.lib.instance"

    def __init__(self, **kwargs):
        """
        Initialize the new object.

        Accepts arbitrary key=value pairs which are filled into the object attributes.
        Then creates an attribute 'config' with a new Config() object.
        """
        super().__init__(**kwargs)
        logging.debug(f"Instance.__init__({kwargs})")
        self.__dict__.update(kwargs)
        self.config = Config()
