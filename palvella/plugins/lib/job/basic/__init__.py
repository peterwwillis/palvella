
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
        self._logger.debug(f"self {self} dict {self.__dict__}")

        self.parse_actions()

        # Register 'receive_alert' function as a hook for all triggers
        self.register_hook('triggers', self.receive_alert)

    async def receive_alert(self, hook, component_instance, message):
        self._logger.debug(f"self: {self}")
        self._logger.debug(f"Received alert:\n\thook {hook}\n\tcomponent_instance {component_instance}\n\tmessage {message}")

    def parse_actions(self):
        if not 'actions' in self.config_data:
            self._logger.debug(f"Warning: no 'actions' found in self.config_data; returning")
            return

        action_objs = self.parent.config.component_ns_config_objects( {"actions": {**self.config_data['actions']}} )
        for action_obj in action_objs:
            self._logger.debug(f"action_obj {action_obj}")
