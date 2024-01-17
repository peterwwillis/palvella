
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.instance import Component
from palvella.lib.instance.mq import MessageQueue, OperationError
from palvella.lib.instance.message import Message

class Trigger(Component, class_type="plugin_base"):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace:       The Python namespace of this plugin module.
        component_namespace:    The namespace in config files for plugins of this class.
    """

    name = None  # A default for child plugins

    plugin_namespace = "palvella.plugins.lib.trigger"
    component_namespace = "triggers"

    async def publish(self, *args, **kwargs):
        """Publish a trigger event to any Message Queues attached to 'self'."""
        ret = await MessageQueue.publish(self, *args, **kwargs)
        return ret

    async def consume(self):
        """Consume a trigger from the Message Queue."""
        ret = await MessageQueue.consume(self)
        return ret

    async def trigger(self, *args, **kwargs):
        """
        Send a trigger to any registered callback functions.

        Any *args* are passed on to the callback function.

        *self*'s 'name', 'plugin_namespace', and 'plugin_type' attributes will be taken and used
        to prepend the message with an Identity Frame, identifying where the trigger originated.
        """

        message = None
        if len(args) == 1 and len(kwargs) < 1:
            if isinstance(args[0], Message):
                message = args[0]
        elif len(args) < 1 and len(kwargs) > 0:
            message = Message(self, **kwargs)
        else:
            raise Exception("Error: trigger() requires either a message argument or a key=value pair set")

        # TODO: Only send a 'publish' if we are configured to send messages to a
        #       Trigger message queue. Otherwise just do the below, running callback
        #       functions within the current process.
        try:
            await self.publish(message)
        except OperationError as e:
            self.logger.exception(f"Tried to publish() but failed: {e}")
            pass

        # TODO: Finish implementing the logic here so that when 'github_webhook' sends
        #       a trigger, it only calls the hooks which have a plugin_dep set for 'github_webhook'.

        for hook, component_instance in self.parent.hooks.match_hook_from_msg(message):
            self.logger.debug(f"matching hook {hook} component_instance {component_instance}")
            await hook.callback(hook, component_instance, message)
