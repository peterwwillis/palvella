
"""The plugin for the Job 'basic'. Defines plugin class and some base functions."""

from palvella.lib.instance.job import Job
from palvella.lib.instance.trigger import Trigger
from palvella.lib.plugin import PluginDependency

PLUGIN_TYPE = "basic"


class BasicJob(Job, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'BasicJob' plugin class."""

    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __pre_plugins__(self):
        self.logger.debug(f"self {self} dict {self.__dict__}")

        self.parse_actions()

        # Register 'receive_alert' function as a hook for all triggers
        self.register_hook('triggers', self.receive_alert)

    def parse_actions(self):
        if not 'actions' in self.config_data:
            self.logger.debug(f"Warning: no 'actions' found in self.config_data; returning")
            return

        self.logger.debug(f"Adding actions for job")
        # TODO: This part isn't right. It's adding the RunAction components to the parent objects,
        #       when really the job needs to maintain its own list of RunActions for that Job.
        #       And going further, maybe these shouldn't even be full-out objects yet, until the
        #       job starts running. What if the list of actions changes during the run?
        #       And how does a DAG of different jobs and actions come into play?
        #       We're probably gonna wanna say 'run this action in this job, then run that action
        #       in that job' (for matrixes?)
        self.parent.components.add_config_components(
            {"actions": {**self.config_data['actions']}},
            self.parent.config.objects
        )
        # TODO: Finish this section. Currently an object is getting created but never initialized.
        #       Also it's on the parent, which is wrong.
        #       Needs some thinking about what to do. See above.
        self.logger.debug(f"Done adding actions from job {self}")
        self.logger.debug(f"self.parent.config.objects: {self.parent.config.objects}")

    async def receive_alert(self, hook, component_instance, message):
        self.logger.info(f"receive_alert(self={self}, hook={hook}, component_instance={component_instance}, message={message})")
        self.logger.info("running job!")
        await self.run_job()

    async def run_job(self):
        self.logger.info("running through each action")

