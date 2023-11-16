
"""The library for frontends. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class Frontend(Component):
    """The 'Frontend' plugin class."""

    plugin_namespace = "palvella.plugins.lib.frontend"
    config_namespace = "frontend"
