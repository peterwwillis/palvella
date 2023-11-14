
"""The library for Actions. Defines plugin class and some base functions."""

from palvella.lib.plugin_base import PluginClass

from .logging import logging


class Action(PluginClass):
    """The 'Action' plugin class."""

    plugin_namespace = "palvella.plugins.lib.action"

    def run(self, **kwargs):
        """Run an action."""
        logging.debug(f"Action.run({kwargs})")
