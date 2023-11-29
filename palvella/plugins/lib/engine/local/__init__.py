
"""The plugin for the Engine 'local'. Defines plugin class and some base functions."""

from palvella.lib.instance.engine import Engine

PLUGIN_TYPE = "local"


class LocalEngine(Engine, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'LocalEngine' plugin class."""
