
from palvella.lib.plugin_base import PluginClass

class Action(PluginClass):
    plugin_namespace = "palvella.plugins.lib.action"

    def run(self, **kwargs):
        print("Action.run(%s)" % kwargs)
