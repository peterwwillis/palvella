
"""The library for message queues. Defines plugin class and some base functions."""

from palvella.lib.instance import Component
from palvella.lib.plugin import PluginDependency


class MessageQueue(Component, class_type="plugin_base"):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    component_namespace = "mq"

    async def publish(self, *args):
        """Publish a message in a message queue."""
        #self._logger.debug(f"MessageQueue.publish({self}, {args})")

    async def consume(self, *args):
        """Consume a message from a queue."""
        #self._logger.debug(f"MessageQueue.consume({self}, {args})")

    @staticmethod
    async def run_func(obj, *args, func=None, **kwargs):
        my_name = None if not hasattr(obj, 'name') else obj.name
        obj_args = [{"name": my_name, "plugin_namespace": obj.plugin_namespace, "plugin_type": obj.plugin_type}]
        my_args = [*obj_args, *args]

        plugin_dep = PluginDependency(parentclass="MessageQueue")
        plugin_components = obj.get_component(plugin_dep)
        obj._logger.debug(f"plugin_components: {plugin_components}")

        results = []
        obj_mq_name = obj.config_data['mq']
        mq_objs = [x for x in plugin_components if x.name == obj_mq_name]
        for component in mq_objs:
            if not hasattr(component, func):
                raise Exception("object {component} does not have function {func}")
            funcref = getattr(component, func)
            obj._logger.debug(f"running {funcref}")
            results.append( await funcref(*my_args, **kwargs) )
        return results
