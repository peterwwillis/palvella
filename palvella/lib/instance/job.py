
"""The library for jobs. Defines plugin class and some base functions."""

from palvella.lib.instance import Instance

from ..logging import logging


class Job(Instance):
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
        logging.debug(f"Job.run({kwargs})")
        for action in self.actions:
            logging.debug(f"  action '{action}'")
