
"""The library for frontends. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance


class Frontend(Instance, class_type="plugin_base"):
    """The 'Frontend' plugin class."""

    plugin_namespace = "palvella.plugins.lib.frontend"
    config_namespace = "frontend"
