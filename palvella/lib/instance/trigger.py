
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.plugin import PluginDependency
from palvella.lib.instance import Component


class Trigger(Component, class_type="plugin_base"):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
    """

    zeromq_dependency = PluginDependency(parentclass="MessageQueue", plugin_type="zeromq")
    depends_on = [ zeromq_dependency ]

    plugin_namespace = "palvella.plugins.lib.trigger"
    config_namespace = "trigger"

    async def publish(self, *, queue="trigger", **kwargs):
        """
        Publish a new trigger to the Message Queue.

        Arguments:
            queue: The name of the queue to send this message to (default 'trigger').
        """
        self._logger.debug(f"Trigger.publish({self}, queue=\"{queue}\", {kwargs})")

        mq = self.get_component(self.zeromq_dependency)
        for obj in mq:
            await obj.publish( queue=queue, **kwargs)

    async def consume(self, *, queue="trigger", **kwargs):
        """
        Consume a trigger Message Queue.
        """

