
"""The library for databases. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class DB(Component):
    """The 'DB' plugin class."""

    plugin_namespace = "palvella.plugins.lib.db"
    config_namespace = "db"
