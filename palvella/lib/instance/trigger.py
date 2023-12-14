
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.plugin import PluginDependency
from palvella.lib.instance import Component
from palvella.lib.instance.mq import MessageQueue


class Trigger(Component, class_type="plugin_base"):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace:       The Python namespace of this plugin module.
        component_namespace:    The namespace in config files for plugins of this class.
    """

    mq_dependency = PluginDependency(parentclass="MessageQueue")
    depends_on = [ mq_dependency ]

    plugin_namespace = "palvella.plugins.lib.trigger"
    component_namespace = "trigger"

    async def publish(self, *args):
        """
        Publish a trigger event to any Message Queues attached to 'self'.
        """
        return await MessageQueue.run_mq_function(self, self.mq_dependency, 'publish', *args)

    async def consume(self, *args):
        """
        Consume a trigger from the Message Queue.
        """
        return await MessageQueue.run_mq_function(self, self.mq_dependency, 'consume', *args)
