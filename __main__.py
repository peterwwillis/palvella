
import ponyans.lib.logging

from ponyans.lib.instance import Instance

from ponyans.lib.db import DB
from ponyans.lib.job import Job
from ponyans.lib.action import Action
from ponyans.lib.engine import Engine


instance = Instance()
instance.config.load(file="foo.yaml")

with open("samples/github_webhook.json") as f:
    instance.trigger( type="github_webhook", data=f.read().decode("utf-8") )

