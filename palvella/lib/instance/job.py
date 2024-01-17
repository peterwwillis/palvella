
"""The library for jobs. Defines plugin class and some base functions."""

from palvella.lib.instance import Component
from palvella.lib.plugin import PluginDependency


class Job(Component, class_type="plugin_base"):
    """
    The 'Job' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
        actions:          A list of Action objects (mandatory).
    """

    plugin_namespace = "palvella.plugins.lib.job"
    component_namespace = "jobs"
    actions = []

    #def run(self, **kwargs):
    #    """Run a Job."""
    #    self.logger.debug(f"Job.run({kwargs})")
    #    for action in self.actions:
    #        self.logger.debug(f"  action '{action}'")

