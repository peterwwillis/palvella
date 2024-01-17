
"""
The logging library. Creates a default logger.

If environment variable 'DEBUG' is true, sets logging level to DEBUG.
"""

import logging
import os

from rich.console import Console
from rich.logging import RichHandler

DEBUG = os.environ.get('DEBUG', '0')
COLOR_LOGGING = os.environ.get('COLOR_LOGGING', '1')
COLOR_LOGGING_WIDTH = os.environ.get('COLOR_LOGGING_WIDTH', '160')

def makeLogger(name):
    colorlog = True if COLOR_LOGGING == "1" else False
    colorlogwidth = int(COLOR_LOGGING_WIDTH, base=10)
    handlers=[]
    if colorlog:
        console = Console(force_terminal=colorlog, width=colorlogwidth)
        handlers = [RichHandler(rich_tracebacks=True, console=console)]
    logging.basicConfig(
            format="%(message)s",
            datefmt="[%X]",
            handlers=handlers
    )
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if DEBUG == "1":
        logger.setLevel(logging.DEBUG)
    return logger
