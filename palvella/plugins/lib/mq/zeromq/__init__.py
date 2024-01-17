
"""The plugin for the Message Queue 'zeromq'. Defines plugin class and some base functions."""

import json
import zmq
import zmq.asyncio
import asyncio

from palvella.lib.instance.mq import MessageQueue, OperationError
from palvella.lib.instance.message import Message

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

    _socket_type_map = { "push": zmq.PUSH,
                         "pull": zmq.PULL,
                         "sub": zmq.SUB,
                         "pub": zmq.PUB,
                         "xsub": zmq.XSUB,
                         "xpub": zmq.XPUB
                       }

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __pre_plugins__(self):
        self.context = zmq.asyncio.Context()

        assert ('socket_type' in self.config_data), "'socket_type' property required in config_data"

        for x in ['name', 'socket_type', 'socket_operation', 'queue', 'identity']:
            if x in self.config_data:
                setattr(self, x, self.config_data[x])

        assert ('url' in self.config_data), "'url' property required in config_data"
        self.url = self.config_data['url']

    def _setup_socket(self):
        """
        Use self.url and self.socket_type to configure a socket.

        If socket_type == "push", socket_operation is set to "connect".
        If socket_type == "pull", socket_operation is set to "bind".
        """

        self.sock = self.context.socket( self._socket_type_map[self.socket_type] )

        if self.socket_operation == None:
            if self.socket_type == "push":
                self.socket_operation = "connect"
            elif self.socket_type == "pull":
                self.socket_operation = "bind"

        self.logger.debug(f"{self}: Running socket operation {self.socket_operation}")
        if self.socket_operation == "connect":
            self.sock.connect(self.url)
        elif self.socket_operation == "bind":
            self.sock.bind(self.url)

        if self.identity != None:
            self.logger.debug(f"setting sockopt(zmq.IDENTITY, {self.identity})")
            self.sock.setsockopt_string(zmq.IDENTITY, self.identity)

        if self.queue == True:
            self.logger.debug(f"setting sockopt(zmq.SUBSCRIBE, {self.name})")
            self.sock.setsockopt_string(zmq.SUBSCRIBE, self.name)

    async def publish(self, message):

        def encode_part(arg):
            if isinstance(arg, dict):
                return json.dumps(arg).encode()
            return arg.encode()

        """
        Publish a Message *message* to the message queue.

        If an entry from *message* is of type 'dict', it is sent as a JSON blob.
        Otherwise it is sent as a binary string.

        The result of zeromq's sock.end_multipart() is returned, which should
        be an object which can be checked to determine if the message was
        received.
        """
        if not self.sock:           self._setup_socket()

        msg_parts = []
        for arg in [message.identity, message.meta]:
            msg_parts.append( encode_part(arg) )
        # message.data is an array of data payloads
        for arg in message.data:
            msg_parts.append( encode_part(arg) )

        self.logger.debug(f"zmq: sending messages ({len(msg_parts)})")

        try:
            res = await self.sock.send_multipart(msg_parts=msg_parts, copy=False)
        except zmq.error.ZMQError as e:
            raise OperationError(e)

        self.logger.debug(f"zmq: sent message, got {res}")
        return res

    async def consume(self, *args):
        """
        Consume a message from a queue.

        Returns a Message() object with the *identity*, *event*, and *data* arguments passed as
        the first, second, and any further frames in the ZeroMQ message.
        (*identity*, *event*, and *data* are decoded as JSON blobs)
        """
        if not self.sock:           self._setup_socket()

        # NOTE: 'copy=False' makes this a non-copying usage, which returns
        #       a frame, not a data payload.
        res = await self.sock.recv_multipart(copy=False)
        self.logger.debug(f"zmq: received message {res}")

        if len(res) < 2:
            raise Exception("message consumed had less than 2 frames")
        identity, event = res[0], res[1]
        data = [json.loads(str(x)) for x in res[2:]] if len(res) > 2 else []

        mqmsg = Message(identity=json.loads(str(identity)), meta=json.loads(str(event)), data=data)
        return mqmsg
