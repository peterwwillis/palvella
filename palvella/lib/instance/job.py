
"""The library for jobs. Defines plugin class and some base functions."""

from palvella.lib.instance import Component


class Job(Component, class_type="plugin_base"):
    """
    The 'Job' plugin class.

    Attributes:
        plugin_namespace: The namespace of this plugin module.
        actions:          A list of Action objects (mandatory).
    """

    plugin_namespace = "palvella.plugins.lib.job"
    config_namespace = "job"
    actions = []

    def run(self, **kwargs):
        """Run a Job."""
        self._logger.debug(f"Job.run({kwargs})")
        for action in self.actions:
            self._logger.debug(f"  action '{action}'")
