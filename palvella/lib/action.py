
"""The library for Actions. Defines plugin class and some base functions."""

from palvella.lib.plugin_base import PluginClass

from .logging import logging


class Action(PluginClass):
    plugin_namespace = "palvella.plugins.lib.action"

    def run(self, **kwargs):
        logging.debug("Action.run({})".format(kwargs))
