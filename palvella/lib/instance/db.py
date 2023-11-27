
"""The library for databases. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance


class DB(Instance, class_type="plugin_base"):
    """The 'DB' plugin class."""

    plugin_namespace = "palvella.plugins.lib.db"
    config_namespace = "db"
