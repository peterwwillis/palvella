
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
        results = []
        self._logger.debug(f"Trigger._run_mq_func({self}, function_name={function_name}, queue=\"{queue}\", {kwargs})")

        mq_components = self.get_component(self.zeromq_dependency)
        self._logger.debug(f"mq_components: {mq_components}")

        mq_name = None
        if 'mq' in self.config_data:
            mq_name = self.config_data['mq']
            self._logger.debug(f"mq_name: {mq_name}")

        mq = []
        for component in mq_components:
            if mq_name != None:
                if component.name == mq_name:
                    self._logger.debug(f"Component {component} matched name, added")
                    mq.append(component) 
            else:
                self._logger.debug(f"Component {component} added")
                mq.append(component)

        for mq_instance in mq:
            if not hasattr(mq_instance, function_name):
                raise Exception("object {mq_instance} does not have function {function_name}")
            func = getattr(mq_instance, function_name)
            self._logger.debug(f"running {func}")
            results.append( await func( queue=queue, **kwargs) )

        return results
