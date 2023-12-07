
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import json
import zmq
import zmq.asyncio
import asyncio

from palvella.lib.instance.mq import MessageQueue

PLUGIN_TYPE = "zeromq"


class ZeroMQ(MessageQueue, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the ZeroMQ message queue plugin. Inherits the MessageQueue class.

       Attributes of 'config_data':
         url:           A URL for a socket to listen on. (ex. "tcp://127.0.0.1:5830")
         socket_type:     Undocumented
    """

    socket_type = None
    sock = None

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()
        #if 'socket_type' in self.config_data:
        #    self.socket_type = self.config_data['socket_type']

    def _setup_socket(self):
        """Use 'url' and self.socket_type to configure a socket."""
        assert ('url' in self.config_data), "'url' property required in config_data"
        if self.socket_type == "push":
            self.sock = self.context.socket(zmq.PUSH)
            self.sock.bind(self.config_data['url'])
        elif self.socket_type == "pull":
            self.sock = self.context.socket(zmq.PULL)
            self.sock.connect(self.config_data['url'])
        else:
            raise Exception("socket_type must be 'push' or 'pull'")

    async def publish(self, *, queue, **kwargs):
        """Publish a dict (kwargs) to the message queue as a JSON document."""
        if not self.socket_type:    self.socket_type = "push"
        if not self.sock:           self._setup_socket()

        queuedict = {"queue": queue}
        newdict = {**queuedict, **kwargs}
        bytesobj = json.dumps(newdict).encode()

        self._logger.debug(f"zmq: sending message")
        res = await self.sock.send(bytesobj)
        self._logger.debug(f"zmq: sent message, got {res}")

    async def consume(self, *, queue, **kwargs):
        """Consume a message from a queue."""
        if not self.socket_type:    self.socket_type = "pull"
        if not self.sock:           self._setup_socket()

        res = await self.sock.recv()
        self._logger.debug(f"\n\nzmq: received message {res}\n\n")
        return res
