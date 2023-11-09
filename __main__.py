import os
import logging

DEBUG = os.environ.get('DEBUG','0')

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
if DEBUG == "1":
    logging.getLogger().setLevel(logging.DEBUG)

import webrunit

from webrunit.lib.db import DB
from webrunit.lib.job import Job
from webrunit.lib.action import Action
from webrunit.lib.engine import Engine


instance = Instance()

db = DB.init(
    name    = "sqlite",
    type    = "sqlite3",
)
instance.load_db(db)

config = Config()
config.load("foo.yaml")
instance.load_configuration()

engine = Engine.init(
    db      = db,
    name    = "local",
    type    = "local"
)

tfjob = Job.init(
    db      =   db,
    name    =   "Terraform job",
    engine  =   "local",
    params  =   [
                    {
                        "name": "account",
                        "description": "The account to deploy Terraform in",
                        "type": "string",
                        "default": "project1"
                    },
                    {
                        "name": "environment",
                        "description": "The environment to deploy Terraform in",
                        "type": "string",
                        "default": "nonprod"
                    }
                ],
    actions =   [
                    Action.init(
                        name="Terraform Plan",
                        type="run", # todo: implement this in the engine
                    )
                ]
)

tfjob.run()

