
"""The library for message queues. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class MessageQueue(Component, class_type="plugin_base"):
    """The 'MessageQueue' plugin class."""

    plugin_namespace = "palvella.plugins.lib.mq"
    component_namespace = "mq"

    async def publish(self, *, queue, **kwargs):
        """Publish a message in a message queue."""
        #self._logger.debug(f"MessageQueue.publish({self}, queue=\"{queue}\", {kwargs})")

    async def consume(self, *, queue, **kwargs):
        """Consume a message from a queue."""
        #self._logger.debug(f"MessageQueue.consume({self}, queue=\"{queue}\", {kwargs})")

    @staticmethod
    async def find_mq_object(obj):
        """
        Given an object, use it to find MessageQueue objects, an 'mq' config_data section,
        and return a specific MQ object.
        """

        mq_components = obj.get_component(obj.mq_dependency)
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
