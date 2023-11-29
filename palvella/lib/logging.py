
"""
The logging library. Creates a default logger.

If environment variable 'DEBUG' is true, sets logging level to DEBUG.
"""

import logging
import os

DEBUG = os.environ.get('DEBUG', '0')

def makeLogger(name):
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if DEBUG == "1":
        logger.setLevel(logging.DEBUG)
    return logger
