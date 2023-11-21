
"""The library for databases. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance


class DB(Instance):
    """The 'DB' plugin class."""

    plugin_namespace = "palvella.plugins.lib.db"
    config_namespace = "db"
