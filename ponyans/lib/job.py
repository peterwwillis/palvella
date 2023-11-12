
from ponyans.lib.plugin_base import PluginClass

class Job(PluginClass):
    plugin_namespace = "ponyans.plugins.lib.job"

    def run(self, **kwargs):
        logging.debug("Job.run(%s)" % kwargs)
        for action in self.actions:
            logging.debug("  action %s" % action)
