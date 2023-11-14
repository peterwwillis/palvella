
import os
import logging

DEBUG = os.environ.get('DEBUG', '0')

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

if DEBUG == "1":
    logging.getLogger().setLevel(logging.DEBUG)
