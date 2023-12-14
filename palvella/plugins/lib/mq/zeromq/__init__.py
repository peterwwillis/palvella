
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
         socket_type:       "push" or "pull". Required.
         socket_operation:  "connect" or "bind". Defaults set based on socket_type.
         sock:              The opened socket
         queue:             Boolean (default: False). Subscribe to a ZeroMQ topic the same as 'name' attribute.
         identity:          A string to use as the 'identity' of a connecting socket.
         config_data:       A dict of configuration data.

       The following attributes come from the 'config_data' attribute dict:
            - name, socket_type, socket_operation, url, queue, identity
    """

    name = None
    url = None
    socket_type = None
    socket_operation = None
    sock = None
    queue = False
    identity = None

    _sock_type_mapping = { "push": zmq.PUSH, "pull": zmq.PULL,
                           "sub": zmq.SUB, "pub": zmq.PUB,
                           "xsub": zmq.XSUB, "xpub": zmq.XPUB
                         }
        

    def __repr__(self):
        return f"ZeroMQ(name={self.name},socket_type={self.socket_type},sock={self.sock},url={self.url})"

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()

        for x in ['name', 'socket_type', 'socket_operation', 'queue', 'identity']:
            if x in self.config_data:
                #self._logger.debug(f"set zeromq attr {x}")
                setattr(self, x, self.config_data[x])

        assert ('url' in self.config_data), "'url' property required in config_data"
        self.url = self.config_data['url']

    def _setup_socket(self):
        """
        Use 'url' and self.socket_type to configure a socket.

        If socket_type == "push", does a connect(url).
        If socket_type == "pull", does a bind(url).
        """

        self.sock = self.context.socket( self._sock_type_mapping[self.socket_type] )

        if self.socket_operation == None:
            if self.socket_type == "push":
                self.socket_operation = "connect"
            elif self.socket_type == "pull":
                self.socket_operation = "bind"

        self._logger.debug(f"{self}: Running socket operation {self.socket_operation}")
        if self.socket_operation == "connect":
            self.sock.connect(self.url)
        elif self.socket_operation == "bind":
            self.sock.bind(self.url)

        if self.identity != None:
            self._logger.debug(f"setting sockopt(zmq.IDENTITY, {self.identity})")
            self.sock.setsockopt_string(zmq.IDENTITY, self.identity)

        if self.queue == True:
            self._logger.debug(f"setting sockopt(zmq.SUBSCRIBE, {self.name})")
            self.sock.setsockopt_string(zmq.SUBSCRIBE, self.name)

    async def publish(self, *args):
        """
        Publish a series of objects (*args) to the message queue.

        Since ZeroMQ supports multipart messages, each of *args is sent as
        a unique message. If an entry is of type 'dict', it is sent as a
        JSON blob. Otherwise it is sent as a string.
        """
        await super().publish(*args)

        if not self.socket_type:    self.socket_type = "push"
        if not self.sock:           self._setup_socket()

        msg_parts = []
        for arg in args:
            if type(arg) == type({}):
                msg_parts.append( json.dumps(arg).encode() )
            else:
                msg_parts.append( arg.encode() )

        self._logger.debug(f"zmq: sending messages: {msg_parts}")
        res = await self.sock.send_multipart(msg_parts=msg_parts, copy=False)
        self._logger.debug(f"zmq: sent message, got {res}")

    async def consume(self, *args):
        """Consume a message from a queue."""
        await super().consume(*args)

        if not self.socket_type:    self.socket_type = "pull"
        if not self.sock:           self._setup_socket()

        # NOTE: 'copy=False' makes this a non-copying usage, which returns
        #       a frame, not a data payload.
        res = await self.sock.recv_multipart(copy=False)
        self._logger.debug(f"zmq: received message {res}")
        return res
