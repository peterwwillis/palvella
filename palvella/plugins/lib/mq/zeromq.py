
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import json
import zmq
import zmq.asyncio

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

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()
        self.sock = self.context.socket(zmq.PUB)
        self.sock.bind(self.url)
        self.parent.mq = self

    async def publish(self, *, queue, **kwargs):
        """Publish a dict (kwargs) to the message queue as a JSON document."""
        newdict = {"queue":queue} + kwargs
        self.sock.send(json.dumps(newdict))

    async def consume(self, *, queue, **kwargs):
        """Consume a message from a queue."""
