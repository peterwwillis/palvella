
from ruamel.yaml import YAML

from webrunit.lib.logging import logging as logging
from webrunit.lib.db import DB
from webrunit.lib.job import Job
from webrunit.lib.action import Action
from webrunit.lib.engine import Engine

class Config(object):

    dbs = []
    engines = []
    jobs = []

    def __init__(self, **kwargs):
        logging.debug("Config.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)

    def load(self, file=None):
        data = None
        if file != None:
            with open(file, "r") as f:
                yaml=YAML(typ='safe')
                return self.parse(yaml.load(f))

    def parse(self, data):

        if 'db' in data:
            assert( type(data['db']) == list ), "'db' value must be a list"
            for db in data['db']:
                self.dbs.append( DB.init( **db ) )

        if 'engine' in data:
            assert( type(data['engine']) == list ), "'engine' value must be a list"
            for engine in data['engine']:
                self.engines.append( Engine.init( **engine ) )

        if 'jobs' in data:
            assert( type(data['jobs']) == list ), "'jobs' value must be a list"
            for job in data['jobs']:
                self.jobs.append( Job.init( **job ) )

