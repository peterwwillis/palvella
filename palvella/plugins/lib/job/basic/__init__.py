
"""The plugin for the Job 'basic'. Defines plugin class and some base functions."""

from palvella.lib.instance.job import Job
from palvella.lib.instance.trigger import Trigger
from palvella.lib.plugin import PluginDependency

PLUGIN_TYPE = "basic"


class BasicJob(Job, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'BasicJob' plugin class."""

    def __pre_plugins__(self):
        self._logger.debug(f"self {self} dict {self.__dict__}")

        # Register 'receive_alert' function as a trigger hook
        self.register_hook('triggers', self.receive_alert)

    async def receive_alert(self, hook, component_instance, message):
        self._logger.debug(f"Received alert: hook {hook} component_instance {component_instance} message {message}")
