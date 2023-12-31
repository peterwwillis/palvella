
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

    def run(self, **kwargs):
        """Run a Job."""
        self._logger.debug(f"Job.run({kwargs})")
        for action in self.actions:
            self._logger.debug(f"  action '{action}'")

    def register_hook(self, component_namespace, callback, hook_type=None):
        """
        Register a hook for a given callback function.

        Arguments:
            component_namespaces:           A list of names of component namespaces.
            callback:                       A function to call.
            hook_type:                      (Optional) The name of the type of hook
                                            being registered.
        """

        if not component_namespace in self.config_data:
            self._logger.debug(f"Warning: could not find component namespace '{component_namespace}' in self.config_data")
            return

        # Register a hook if this component (Job) has been configured
        # with a component namespace section, and a particular plugin type in each
        # section. Basically the configuration determines what plugins can trigger
        # this job.
        for plugin_type, data in self.config_data[component_namespace].items():
            for item in data:
                plugin_dep = PluginDependency(component_namespace=component_namespace, plugin_type=plugin_type)
                self.parent.hooks.register_hook(
                    plugin_dep=plugin_dep,
                    hook_type=hook_type,
                    callback=self.receive_alert,
                    data=item
                )
