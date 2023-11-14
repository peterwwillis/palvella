
from palvella.lib.action import Action
from palvella.lib.logging import logging as logging

type = "run"


class RunAction(Action):
    type = type

    def __init__(self, **kwargs):
        logging.debug(f"RunAction({kwargs})")
        self.__dict__.update(kwargs)


classref = RunAction
logging.debug("Loaded plugin RunAction()")
