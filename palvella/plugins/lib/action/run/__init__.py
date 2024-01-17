
"""The plugin for the Action 'run'. Defines plugin class and some base functions."""

from palvella.lib.instance.action import Action

PLUGIN_TYPE = "run"


class RunAction(Action, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'RunAction' plugin class."""

    def __pre_plugins__(self):
        self.logger.debug(f"self {self} config_data {self.config_data}")
        #self.register_hook('actions', self.receive_alert)

    async def receive_alert(self, hook, component_instance, message):
        self.logger.debug(f"self: {self}")

