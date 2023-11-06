
import logging

#from webrunit.lib.engine.base import Engine

def init():
    return LocalEngine

class LocalEngine(object):
    type = "local"

    def __init__(self, **kwargs):
        logging.debug("new LocalEngine('%s') created" % (kwargs))

logging.debug("Loaded plugin LocalEngine()")
