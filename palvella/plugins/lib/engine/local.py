
from palvella.lib.engine.base import Engine
from palvella.lib.logging import logging as logging

type = "local"


class LocalEngine(Engine):
    type = type

    def __init__(self, **kwargs):
        logging.debug("LocalEngine(%s)" % kwargs)
        self.__dict__.update(kwargs)


classref = LocalEngine
logging.debug("Loaded plugin LocalEngine()")
