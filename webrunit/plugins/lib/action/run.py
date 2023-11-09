
from webrunit.lib.logging import logging as logging
from webrunit.lib.action.base import Action

type = "run"

class RunAction(Action):
    type = type

    def __init__(self, **kwargs):
        logging.debug("RunAction(%s)" % (kwargs))
        self.__dict__.update(kwargs)

classref = RunAction
logging.debug("Loaded plugin RunAction()")
