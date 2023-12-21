
"""The plugin for the Job 'basic'. Defines plugin class and some base functions."""

from palvella.lib.instance.job import Job
from palvella.lib.instance.trigger import Trigger

PLUGIN_TYPE = "basic"


class BasicJob(Job, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'BasicJob' plugin class."""

    def __pre_plugins__(self):
        self._logger.debug(f"self {self} dict {self.__dict__}")

        for plugin_base in ['triggers']:
            if not plugin_base in self.config_data:
                continue
            for plugin_type, data in self.config_data[plugin_base].items():
                for item in data:
                    self.parent.hooks.register_hook(component_ns=plugin_base, plugin_type=plugin_type,
                                       hook_type="event", hook=self.receive_alert, match_data=item)

    def receive_alert(self, alert):
        self._logging.debug(f"Received alert: {alert}")
