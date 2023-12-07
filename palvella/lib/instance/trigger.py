
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
        self._logger.debug(f"Trigger._run_mq_func({self}, function_name={function_name}, queue=\"{queue}\", {kwargs})")

        mq = self.get_component(self.zeromq_dependency)
        results = []
        for obj in mq:
            if not hasattr(obj, function_name):
                raise Exception("object {obj} does not have function {function_name}")
            func = getattr(obj, function_name)
            results.append( await func( queue=queue, **kwargs) )
        return results
