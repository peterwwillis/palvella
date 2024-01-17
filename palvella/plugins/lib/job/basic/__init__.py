
"""The plugin for the Job 'basic'. Defines plugin class and some base functions."""

from palvella.lib.instance.job import Job
from palvella.lib.instance.trigger import Trigger
from palvella.lib.plugin import PluginDependency

PLUGIN_TYPE = "basic"


class BasicJob(Job, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'BasicJob' plugin class."""

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __pre_plugins__(self):
        self.logger.debug(f"self {self} dict {self.__dict__}")

        self.parse_actions()

        # Register 'receive_alert' function as a hook for all triggers
        self.register_hook('triggers', self.receive_alert)

    async def receive_alert(self, hook, component_instance, message):
        self.logger.debug(f"self: {self}")
        self.logger.debug(f"Received alert:\n\thook {hook}\n\tcomponent_instance {component_instance}\n\tmessage {message}")

    def parse_actions(self):
        if not 'actions' in self.config_data:
            self.logger.debug(f"Warning: no 'actions' found in self.config_data; returning")
            return

        self.parent.components.add_config_components(
            {"actions": {**self.config_data['actions']}},
            self.parent.config.objects
        )
        # TODO: Finish this section. Currently an object is getting created but never initialized.
        #       Needs some thinking about what to do.
        self.logger.debug(f"Done adding actions from job {self}")
