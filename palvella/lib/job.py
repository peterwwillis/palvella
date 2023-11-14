
from .logging import logging
from palvella.lib.plugin_base import PluginClass


class Job(PluginClass):
    plugin_namespace = "palvella.plugins.lib.job"

    def run(self, **kwargs):
        logging.debug("Job.run(%s)" % kwargs)
        for action in self.actions:
            logging.debug("  action %s" % action)