
"""The library for Actions. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class Action(Component, class_type="plugin_base"):
    """The 'Action' plugin class."""

    plugin_namespace = "palvella.plugins.lib.action"
    component_namespace = "actions"

    def run(self, **kwargs):
        """Run an action."""
        self.logger.debug(f"Action.run({kwargs})")
