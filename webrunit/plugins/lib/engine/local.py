
from webrunit.lib.logging import logging as logging
from webrunit.lib.engine.base import Engine

type = "local"

class LocalEngine(Engine):
    type = type

    def __init__(self, **kwargs):
        logging.debug("LocalEngine(%s)" % kwargs)
        self.__dict__.update(kwargs)

classref = LocalEngine
logging.debug("Loaded plugin LocalEngine()")
