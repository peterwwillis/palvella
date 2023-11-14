
"""The plugin for the Engine 'local'. Defines plugin class and some base functions."""

from palvella.lib.engine import Engine
from palvella.lib.logging import logging

TYPE = "local"


class LocalEngine(Engine):
    """
    The 'LocalEngine' plugin class.

    Attributes:
        TYPE: The name of the type of this Action plugin.
    """

    TYPE = TYPE


ClassRef = LocalEngine
logging.debug("Loaded plugin LocalEngine()")
