
"""The library for message queues. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


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
    async def find_mq_object(obj, dependencies):
        """
        Given a plugin object, look up any loaded MessageQueue components.
        Also within the plugin object, look for an 'mq' section in the 'config_data' attribute.
        Return any objects with the same name as the 'mq' section, or if there's no
        'mq' section at all, return all loaded MessageQueue objects.
        """

        mq_components = obj.get_component(dependencies)
        obj._logger.debug(f"mq_components: {mq_components}")

        mq_name = None
        if 'mq' in obj.config_data:
            mq_name = obj.config_data['mq']
            obj._logger.debug(f"mq_name: {mq_name}")

        mq = []
        for component in mq_components:
            if mq_name != None:
                if component.name == mq_name:
                    obj._logger.debug(f"Component {component} matched name, added")
                    mq.append(component)
            else:
                obj._logger.debug(f"Component {component} added")
                mq.append(component)
        return mq

    @staticmethod
    async def run_mq_function(obj, dependencies, function_name, *args):
        """
        Run a message queue function for a plugin.

        Pass a plugin object 

        If the plugin has a 'config_data' attribute with an 'mq' key, the value is considered
        the name of a loaded MessageQueue object to use. That object is used to send and receive
        MessageQueue items.
        """

        results = []
        obj._logger.debug(f"run_mq_function({obj}, function_name={function_name}, {args})")

        mq = await MessageQueue.find_mq_object(obj, dependencies)
        for mq_instance in mq:
            if not hasattr(mq_instance, function_name):
                raise Exception("object {mq_instance} does not have function {function_name}")
            func = getattr(mq_instance, function_name)
            obj._logger.debug(f"running {func}")
            results.append( await func( *args) )

        return results
