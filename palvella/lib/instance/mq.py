
"""The library for message queues. Defines plugin class and some base functions."""

from dataclasses import dataclass

from palvella.lib.instance import Component
from palvella.lib.instance.message import Message
from palvella.lib.plugin import PluginDependency

from ..logging import makeLogger, logging

class OperationError(Exception):
    """Raise an error during an operation of a message queue."""
    def __init__(self, obj):
        if type(obj) != type(str) and hasattr(obj, '__dict__'):
            self.__dict__ = {**self.__dict__, **obj.__dict__}
        super().__init__(obj)


class MessageQueue(Component, class_type="plugin_base"):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    component_namespace = "mq"

    logger = makeLogger(__module__ + "/MessageQueue")

    @classmethod
    async def publish(cls, obj, *args, **kwargs):
        """
        Publish a message in a message queue.

        Uses the 'run_func' function (of this class) to call the "publish" function of MessageQueue components.
        """

        cls.logger.info(f"publish(obj={obj}, args={args}, kwargs={kwargs})")
        return await MessageQueue.run_func(obj, *args, func="publish", **kwargs)

    @classmethod
    async def consume(cls, obj, *args, **kwargs):
        """Consume a message from a queue. Returns MessageQueue.consume()"""

        cls.logger.info(f"consume(obj={obj}, args={args}, kwargs={kwargs})")
        return await MessageQueue.run_func(obj, *args, func="consume", **kwargs)

    @staticmethod
    async def run_func(obj, *args, func=None, **kwargs):
        """
        A wrapper to locate a MessageQueue component instance and run a particular function.

        Arguments:
            func (required):    A function of the MessageQueue component to call, passing
                                *args* and *kwargs*.
            args:               Positional arguments.
            kwargs:             key=value arguments.

        All loaded components are scanned for a parent class MessageQueue. Of those,
        if any of them have a *name* attribute, and it matches *obj.config_data['mq']*,
        assume that component is the MessageQueue the object wants to run *func* on.
        """
        results = []

        assert (func != None), f"Error: 'func' must not be None."

        # Find all instances of components that match MessageQueue
        plugin_dep = PluginDependency(parentclass="MessageQueue")
        plugin_components = obj.get_component(plugin_dep)

        mq_objs = [x for x in plugin_components if x.name == obj.config_data['mq'] ]
        for component in mq_objs:
            if not hasattr(component, func):
                raise Exception("object {component} does not have function {func}")
            funcref = getattr(component, func)
            obj.logger.debug(f"run_func: running {funcref}")
            results.append( await funcref(*args, **kwargs) )

        return results
