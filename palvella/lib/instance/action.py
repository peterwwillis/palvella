
"""The library for Actions. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance

from ..logging import logging


class Action(Instance):
    """The 'Action' plugin class."""

    plugin_namespace = "palvella.plugins.lib.action"
    config_namespace = "action"

    def run(self, **kwargs):
        """Run an action."""
        logging.debug(f"Action.run({kwargs})")
