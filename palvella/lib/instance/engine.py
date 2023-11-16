
"""The library for engines. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class Engine(Component):
    """The 'Engine' plugin class."""

    plugin_namespace = "palvella.plugins.lib.engine"
    config_namespace = "engine"
