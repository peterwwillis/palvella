
"""The library for message queues. Defines plugin class and some base functions."""

from dataclasses import dataclass

from palvella.lib.instance import Component
from palvella.lib.plugin import PluginDependency


@dataclass
class MQMessage:
    """
    A message received from the message queue.

    Arguments:
        identity:           The sender of the message.
        event:              A multi-dimensional dict of metadata about the event received.
          mq:               Message Queue-specific metadata.
            event_type:     The type of event this is. Options: "trigger"
        data:               Payload data
    """
    identity = None
    event = None
    data = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class MessageQueue(Component, class_type="plugin_base"):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    component_namespace = "mq"

    @staticmethod
    async def publish(obj, *args):
        """Publish a message in a message queue."""

        # The first frame in the message will have the following structure.
        # The intent is to identify what sent the message/the message context.
        my_name = None if not hasattr(obj, 'name') else obj.name
        obj_args = [
            {
                "name": my_name,
                "plugin_namespace": obj.plugin_namespace,
                "plugin_type": obj.plugin_type
            }
        ]
        my_args = [*obj_args, *args]

        return await MessageQueue.run_func(obj, *my_args, func="publish")

    @staticmethod
    async def consume(obj):
        """Consume a message from a queue."""
        return await MessageQueue.run_func(obj, func="consume")

    @staticmethod
    async def run_func(obj, *args, func=None, **kwargs):
        """A wrapper to locate a MessageQueue component instance and run a particular function."""
        results = []

        # Find all instances of components that match MessageQueue
        plugin_dep = PluginDependency(parentclass="MessageQueue")
        plugin_components = obj.get_component(plugin_dep)
        #obj._logger.debug(f"plugin_components: {plugin_components}")
        mq_objs = [x for x in plugin_components if x.name == obj.config_data['mq'] ]

        for component in mq_objs:
            if not hasattr(component, func):
                raise Exception("object {component} does not have function {func}")
            funcref = getattr(component, func)
            obj._logger.debug(f"run_func: running {funcref}")
            results.append( await funcref(*args, **kwargs) )

        return results
