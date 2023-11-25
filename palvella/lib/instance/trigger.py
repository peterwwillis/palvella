
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance
from palvella.lib.logging import logging


class Trigger(Instance):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
    """

    plugin_namespace = "palvella.plugins.lib.trigger"
    config_namespace = "trigger"

    async def publish(self, *, queue="trigger", **kwargs):
        """
        Publish a new trigger to the Message Queue.

        Arguments:
            queue: The name of the queue to send this message to (default 'trigger').
        """
        logging.debug(f"Trigger.publish({self}, queue=\"{queue}\", {kwargs})")

        if hasattr(self, "mq"):
            await self.instance.mq.publish( name=self.mq, queue=queue, **kwargs)
        else:
            raise Exception("error: currently require Trigger object to have self.mq defined")

    async def consume(self, *, queue="trigger", **kwargs):
        """
        Consume a trigger Message Queue.
        """

