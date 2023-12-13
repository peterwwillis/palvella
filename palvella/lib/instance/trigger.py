
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

    async def publish(self, *, queue="trigger", **kwargs):
        """
        Publish a trigger to the Message Queue.

        Arguments:
            queue: The name of the queue to send this message to (default 'trigger').
        """
        return await self._run_mq_func('publish', queue=queue, **kwargs)

    async def consume(self, *, queue="trigger", **kwargs):
        """
        Consume a trigger from the Message Queue.

        Arguments:
            queue: The name of the queue to send this message to (default 'trigger').
        """
        return await self._run_mq_func('consume', queue=queue, **kwargs)

    async def _run_mq_func(self, function_name, *, queue="trigger", **kwargs):
        """
        Run a message queue function for a Trigger plugin.

        If the plugin has a 'config_data' attribute with an 'mq' key, the value is considered
        the name of a loaded MessageQueue object to use. That object is used to send and receive
        MessageQueue items.
        """

        results = []
        self._logger.debug(f"Trigger._run_mq_func({self}, function_name={function_name}, queue=\"{queue}\", {kwargs})")

        mq = await MessageQueue.find_mq_object(self)
        for mq_instance in mq:
            if not hasattr(mq_instance, function_name):
                raise Exception("object {mq_instance} does not have function {function_name}")
            func = getattr(mq_instance, function_name)
            self._logger.debug(f"running {func}")
            results.append( await func( queue=queue, **kwargs) )

        return results
