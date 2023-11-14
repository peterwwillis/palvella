
from .logging import logging
from palvella.lib.plugin_base import PluginClass


class Action(PluginClass):
    plugin_namespace = "palvella.plugins.lib.action"

    def run(self, **kwargs):
        logging.debug("Action.run({})".format(kwargs))
