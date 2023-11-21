
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import zmq

from palvella.lib.instance.mq import MessageQueue
from palvella.lib.logging import logging

TYPE = "zeromq"


class ZeroMQ(MessageQueue):
    """
    Class of the ZeroMQ message queue plugin. Inherits the MessageQueue class.

    Attributes of this class:
        'TYPE'      - The name of the type of this database.
    """

    TYPE = TYPE

    async def instance_init(self, **kwargs):
        self.instance.mq = self
        logging.debug(f"ZeroMQ instance {self.instance} mq {self.instance.mq}")
