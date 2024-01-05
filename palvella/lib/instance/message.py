"""Defines messages for IPC."""

import json
from dataclasses import dataclass
from collections import UserList

from ..logging import makeLogger


@dataclass
class Message:
    """
    A message to pass between IPC components.

    Arguments:
        identity:               The sender of the message. This is detected automatically from
                                the object passed as the constructor's first argument.
          name:                 Name of the sender of the message.
          plugin_namespace:     The plugin namespace of the sender.
          plugin_type:          The plugin type of the sender.
        meta:                   A multi-dimensional dict of metadata about the
                                event received.  Each key's value should be a dict.
        data:                   Payload data.
    """

    _logger = makeLogger(__module__ + "/Message")

    @dataclass
    class Identity:
        """Keep the identity of the message.

        Pass either a dict, or a set of key=value arguments, to set the identity data.

        Arguments:
            name:                   Name of the object that created the message.
            plugin_namespace:       Plugin namespace of the object that created the message.
            plugin_type:            Plugin type of the object that created the message.
        """

        def __repr__(self):
            return "%s(%r)" % (self.__class__, self.__dict__)

        def __init__(self, *args, **kwargs):
            if len(args) == 1 and len(kwargs) < 1:
                if not isinstance(args[0], dict):
                    raise Exception("Invalid argument {args[0]} to Identity()")
                self.__update_kv__(args[0])
            elif len(args) < 1 and len(kwargs) > 0:
                self.__update_kv__(kwargs)
            else:
                raise Exception("Invalid arguments to Identity(): must be either one arg (type dict), or a kwargs dict")

        def __update_kv__(self, kv):
            for arg in kv.keys():
                if arg not in ["name", "plugin_namespace", "plugin_type"]:
                    raise Exception(f"Error: Identity attribute names must be one of 'name', 'plugin_namespace', 'plugin_type' (got '{arg}')")
            self.__dict__.update(kv)

        def encode(self):
            """Return a binary encoding of the Identity data as a JSON blob."""
            return json.dumps(self.__dict__).encode()

    @dataclass
    class Meta:
        """Keeps a multi-dimensional dict of metadata."""

        def __repr__(self):
            return "%s(%r)" % (self.__class__, self.__dict__)

        def __init__(self, kv):
            for k, v in kv.items():
                assert ( isinstance(v, dict) ), f"Error: attribute 'meta' key '{k}' value must be a dict (was {type(v)})"
            self.__dict__.update(kv)

        def encode(self):
            """Return a binary encoding of the metadata as a JSON blob."""
            return json.dumps(self.__dict__).encode()

    @dataclass
    class Data(UserList):
        """Keeps a list of data. Iterable."""

        _ctr = 0

        def __init__(self, args=[]):
            assert ( isinstance(args, list) ), "Error: Data class argument must be a list"
            return super().__init__(args)

        def __repr__(self):
            return f"{self.__class__}(CONCEALED)"

        def __iter__(self):
            return self

        def __next__(self):
            self._ctr += 1
            try:
                return self.data[self._ctr-1]
            except IndexError:
                self._ctr = 0
                raise StopIteration

        def encode(self):
            """Return a binary encoding of the data array as a JSON blob.

            NOTE: Once encoded this way, it may appear that the data originally
            included an array as the first element, when in fact the outer
            array in the encoded JSON is the array this class uses to keep all
            the data items. The outer array must later be unpacked and
            considered separate from the data itself."""
            return json.dumps(self.data).encode()


    def __init__(self, parentobj=None, **kwargs):
        if 'identity' in kwargs.keys():
            self.identity = self.Identity(kwargs['identity'])
        else:
            self.identity = self.Identity({
                "name": parentobj.name if hasattr(parentobj, 'name') else None,
                "plugin_namespace": parentobj.plugin_namespace,
                "plugin_type": parentobj.plugin_type
            })

        if not 'meta' in kwargs.keys():
            raise Exception("Missing argument to Message(): 'meta'")
        self.meta = self.Meta(kwargs['meta'])

        self.data = self.Data()
        if 'data' in kwargs.keys():
            #self._logger.debug(f"setting data as {kwargs['data']}")
            self.data = self.Data(kwargs['data'])

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)
