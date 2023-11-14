
from ruamel.yaml import YAML

from palvella.lib.plugin_base import PluginClass

from .logging import logging
from .db import DB
from .job import Job
from .action import Action
from .engine import Engine
from .trigger import Trigger


class Config(object):

    dbs = []
    engines = []
    jobs = []

    def __init__(self, **kwargs):
        logging.debug("Config.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)

    def load(self, file=None):
        if file is not None:
            with open(file, "r") as f:
                yaml = YAML(typ='safe')
                return self.parse(yaml.load(f))

    def parse(self, data):

        if 'db' in data:
            assert (data['db'] is list), "'db' value must be a list"
            for db in data['db']:
                self.dbs.append(DB.init(**db))

        if 'engine' in data:
            assert (data['engine'] is list), "'engine' value must be a list"
            for engine in data['engine']:
                self.engines.append(Engine.init(**engine))

        if 'jobs' in data:
            assert (data['jobs'] is list), "'jobs' value must be a list"
            for job in data['jobs']:
                self.jobs.append(Job.init(**job))

        if 'triggers' in data:
            assert (data['jobs'] is list), "'jobs' value must be a list"
            for trigger in data['triggers']:
                self.triggers.append(Trigger.init(**trigger))


class Instance(PluginClass):
    plugin_namespace = "palvella.plugins.lib.instance"

    def __init__(self, **kwargs):
        logging.debug("Instance.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)
        self.config = Config()
