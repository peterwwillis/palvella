
"""The library for message queues. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class MessageQueue(Component, class_type="plugin_base"):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    config_namespace = "mq"

    async def publish(self, *, name, queue, **kwargs):
        """Publish a message in a message queue."""
        self._logger.debug(f"MessageQueue.publish({self}, name=\"{name}\", queue=\"{queue}\", {kwargs})")

    async def consume(self, *, name, queue, **kwargs):
        """Consume a message from a queue."""
        self._logger.debug(f"MessageQueue.consume({self}, name=\"{name}\", queue=\"{queue}\", {kwargs})")
