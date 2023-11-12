
from ponyans.lib.logging import logging as logging
from .config.base import Config

class Instance(object):

    def __init__(self, **kwargs):
        logging.debug("Instance.__init__(%s)" % kwargs)
        self.__dict__.update(kwargs)
        self.config = Config()
