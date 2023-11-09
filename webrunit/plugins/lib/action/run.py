
import logging

from webrunit.lib.action.base import Action

def init():
    return RunAction

class RunAction(Action):
    type = "run"

    def __init__(self, **kwargs):
        logging.debug("RunAction(%s)" % (kwargs))
        self.__dict__.update(kwargs)

logging.debug("Loaded plugin RunAction()")
