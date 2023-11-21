
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.logging import logging
from palvella.lib.instance import Instance


class Trigger(Instance):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
    """

    plugin_namespace = "palvella.plugins.lib.trigger"
    config_namespace = "trigger"

    async def publish(self, **kwargs):
        """Publish a new trigger in the Message Queue."""
        logging.debug(f"Trigger.publish({self}, {kwargs})")
        await self.instance.mq.publish( queue="trigger", **kwargs)
