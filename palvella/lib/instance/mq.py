
"""The library for message queues. Defines plugin class and some base functions."""

from palvella.lib.logging import logging
from palvella.lib.instance import Instance


class MessageQueue(Instance):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    config_namespace = "mq"

    async def publish(self, **kwargs):
        """Publish a message in a message queue."""
        logging.debug(f"MessageQueue({self}, {kwargs})")
