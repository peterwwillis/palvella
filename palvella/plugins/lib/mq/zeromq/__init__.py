
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import json
import zmq
import zmq.asyncio
import asyncio

from palvella.lib.instance.mq import MessageQueue

PLUGIN_TYPE = "zeromq"


class ZeroMQ(MessageQueue, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the ZeroMQ message queue plugin. Inherits the MessageQueue class.

       Attributes of the object:
         name:              The name of this ZeroMQ instance.
         url:               A URL for a socket to listen on. (ex. "tcp://127.0.0.1:5830")
         socket_type:       "push" or "pull"
         sock:              The opened socket
         config_data:       A dict of configuration data.

       The following attributes come from the 'config_data' attribute:
            - name, socket_type, url
    """

    name = None
    url = None
    socket_type = None
    sock = None

    def __repr__(self):
        return f"ZeroMQ(name={self.name},socket_type={self.socket_type},sock={self.sock},url={self.url})"

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()
        if 'name' in self.config_data:
            self.name = self.config_data['name']
        if 'socket_type' in self.config_data:
            self.socket_type = self.config_data['socket_type']
        assert ('url' in self.config_data), "'url' property required in config_data"
        self.url = self.config_data['url']

    def _setup_socket(self):
        """Use 'url' and self.socket_type to configure a socket."""
        if self.socket_type == "push":
            self._logger.debug(f"{self}: Setting up self.sock.connect({self.url})")
            self.sock = self.context.socket(zmq.PUSH)
            #self.sock.bind(self.url)
            self.sock.connect(self.url)
        elif self.socket_type == "pull":
            self._logger.debug(f"{self}: Setting up self.sock.bind({self.url})")
            self.sock = self.context.socket(zmq.PULL)
            #self.sock.connect(self.url)
            self.sock.bind(self.url)
        else:
            raise Exception("socket_type must be 'push' or 'pull'")

    async def publish(self, *, queue, **kwargs):
        """Publish a dict (kwargs) to the message queue as a JSON document."""
        await super().publish(queue=queue, **kwargs)

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
        await super().consume(queue=queue, **kwargs)

        if not self.socket_type:    self.socket_type = "pull"
        if not self.sock:           self._setup_socket()

        # NOTE: 'copy=False' makes this a non-copying usage, which returns
        #       a frame, not a data payload.
        res = await self.sock.recv(copy=False)
        self._logger.debug(f"\n\nzmq: received message {res}\n\n")
        return res
