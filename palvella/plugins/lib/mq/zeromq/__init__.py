
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import json
import zmq
import zmq.asyncio

from palvella.lib.instance.mq import MessageQueue

PLUGIN_TYPE = "zeromq"


class ZeroMQ(MessageQueue, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the ZeroMQ message queue plugin. Inherits the MessageQueue class."""

    url = None  # "tcp://127.0.0.1:5680"

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()
        self.sock = self.context.socket(zmq.PUB)

        if self.url:
            self.sock.bind(self.url)
        self.parent.mq = self

    async def publish(self, *, queue, **kwargs):
        """Publish a dict (kwargs) to the message queue as a JSON document."""
        queuedict = {"queue": queue}
        newdict = {**queuedict, **kwargs}
        bytesobj = json.dumps(newdict).encode()
        self.sock.send(bytesobj)

    async def consume(self, *, queue, **kwargs):
        """Consume a message from a queue."""
