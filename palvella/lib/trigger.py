
"""The library for triggers. Defines plugin class and some base functions."""

from palvella.lib.plugin_base import PluginClass


class Trigger(PluginClass):
    """
    The 'Trigger' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
    """

    plugin_namespace = "palvella.plugins.lib.trigger"
