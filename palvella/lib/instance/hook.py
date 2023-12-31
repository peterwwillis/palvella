
"""The base class for Hooks. This is currently only used by Instance class."""

from dataclasses import dataclass

from palvella.lib.plugin import match_class_dependencies
from palvella.lib.instance.message import Message

from ..logging import makeLogger, logging

_logger = makeLogger(__name__)


@dataclass
class Hook:
    component = None
    hook_type = None
    callback = None
    data = None
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)


class Hooks:
    """
    Manages hooks for components.

    Attributes:
        parent:         A reference to the parent Instance() object.
    """

    _hooks = []

    def __init__(self, parent):
        self.parent = parent

    def list(self):
        return self._hooks

    def register_hook(self, plugin_dep, hook_type, callback, data):
        """
        Register a callback function to match against a plugin dependency if matching *data* is found.

        For each class matching *plugin_dep* PluginDependency, register a callback function, hook type,
        and data. The match_hook() function can be used to compare this hook against objects.

        """
        _logger.debug(f"register_hook({self}, {plugin_dep}, {hook_type}, {callback}, {data})")

        components = match_class_dependencies(self, self.parent.plugins.classes, [plugin_dep])
        for component in components:
            self._hooks.append(
                Hook(component=component, hook_type=hook_type, callback=callback, data=data)
            )

    def match_hook_from_msg(self, msg):
        """
        Look for a hookBased on an Message() *msg*, return hook and component instances that match.

        Looks for component instances that match registered hooks.
        Compares the hook data section against a *msg* (Message) data section.
        If the data matches, the hook and component instance are yielded.

        Arguments:
            msg:            An object
              msg.data:     A dict to compare against each hook's *data* attribute
        """
        assert ( isinstance(msg, Message) ), "Requires Message object argument"

        for hook in self.parent.hooks.list():
            for instance in self.parent.components.instances:

                if hook.component.plugin_namespace != instance.plugin_namespace \
                   or hook.component.plugin_type != instance.plugin_type:
                    continue
                _logger.debug(f"match_hook: Found component instance {instance} matching hook component {hook.component}")

                if hook.component.plugin_namespace != msg.identity.plugin_namespace \
                   or hook.component.plugin_type != msg.identity.plugin_type:
                    continue
                _logger.debug(f"match_hook: Found hook {hook} matches msg {msg.identity}")

                if not self.match_hook_data(hook=hook, component_instance=instance, msg=msg):
                    continue
                _logger.debug(f"match_hook: hook data matches msg data")

                yield hook, instance

    def match_hook_data(self, hook, component_instance, msg):
        """
        Compare a Hook() data section against an Message() data array.

        Uses compareDict() to recursively verify that *hook.data* entries exist in
        *msg[].data*.

        If both the hook and message data are not dicts, returns True.
        If both hook and message data are dicts, and the hook data does not exist
        in the message data, returns False.
        Otherwise returns True.
        """
        for data in msg.data:
            if not isinstance(hook.data, dict) and not isinstance(data, dict):
                return True
            if not compareDict(hook.data, data):
                return False
        return True


def compareDict(d1, d2):
    for k in d1:
        if not k in d2:
            return False
        if isinstance(d1[k], dict) and isinstance(d2[k], dict):
            return compareDict(d1[k],d2[k])
        if d1[k] != d2[k]:
            return False
    return True
