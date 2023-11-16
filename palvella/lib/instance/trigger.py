
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class Trigger(Component):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
    """

    plugin_namespace = "palvella.plugins.lib.trigger"
    config_namespace = "trigger"
