
"""The plugin for the Job 'default'. Defines plugin class and some base functions."""

from palvella.lib.instance.job import Job

PLUGIN_TYPE = "default"


class DefaultJob(Job, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'DefaultJob' plugin class."""
