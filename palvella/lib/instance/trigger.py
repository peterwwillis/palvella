
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.instance import Component
from palvella.lib.instance.mq import MessageQueue, MQMessage


class Trigger(Component, class_type="plugin_base"):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace:       The Python namespace of this plugin module.
        component_namespace:    The namespace in config files for plugins of this class.
    """

    name = None  # A default for child plugins

    plugin_namespace = "palvella.plugins.lib.trigger"
    component_namespace = "triggers"

    async def publish(self, *args):
        """Publish a trigger event to any Message Queues attached to 'self'."""
        ret = await MessageQueue.publish(self, *args)
        return ret

    async def consume(self):
        """Consume a trigger from the Message Queue."""
        ret = await MessageQueue.consume(self)
        return ret

    async def trigger(self, *args):
        """Trigger hooks based on a Message Queue message."""
        for arg in args:
            assert ( isinstance(arg, MQMessage) ), f"Error: msg {arg} must be MQMessage"
            for hook in self.parent.hooks.match_hook(arg):
                self._logger.debug(f"matching hook {hook}")

