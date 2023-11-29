
"""The plugin for the Action 'run'. Defines plugin class and some base functions."""

from palvella.lib.instance.action import Action

PLUGIN_TYPE = "run"


class RunAction(Action, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'RunAction' plugin class."""
