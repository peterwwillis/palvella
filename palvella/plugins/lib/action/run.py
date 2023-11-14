
"""The plugin for the Action 'run'. Defines plugin class and some base functions."""

from palvella.lib.action import Action
from palvella.lib.logging import logging

TYPE = "run"


class RunAction(Action):
    """
    The 'RunAction' plugin class.

    Attributes:
        TYPE: The name of the type of this Action plugin.
    """

    TYPE = TYPE


ClassRef = RunAction
logging.debug("Loaded plugin RunAction()")
