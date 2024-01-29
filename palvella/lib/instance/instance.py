
"""The base class for the Instance. Defines plugin class and some base functions."""

from palvella.lib.instance.config import loadYamlFile, Config
from palvella.lib.instance.component import Component, ComponentObjects
from palvella.lib.plugin import Plugin, WalkPlugins
from palvella.lib.instance.hook import Hooks
from ..logging import makeLogger, logging


logger = makeLogger(__name__)


class Instance(Plugin, class_type="base"):
    """The 'Instance' plugin class. Creates a new instance of the application."""

    plugin_namespace = "palvella.lib.instance"

    hooks = None
    plugins = None
    components = None
    config = None
    config_path = None
    config_data = None

    def __init__(self, config_path=None, config_data=None):
        super().__init__()

        self.config_path = config_path
        self.config_data = config_data
        self.hooks = Hooks(parent=self)

        # Load plugin subclasses from the 'Component' class
        self.plugins = WalkPlugins(Component)

        self.config = Config(parent=self, config_path=self.config_path, 
                             config_data=self.config_data)

    async def initialize(self):
        """Initialize the new instance."""
        if self.config:
            self.components = ComponentObjects(root=self, parent=self, config=self.config)
            await self.components.initialize()
