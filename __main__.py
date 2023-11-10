
import webrunit.lib.logging

from webrunit.lib.instance import Instance

from webrunit.lib.db import DB
from webrunit.lib.job import Job
from webrunit.lib.action import Action
from webrunit.lib.engine import Engine


instance = Instance()
instance.config.load(file="foo.yaml")

with open("samples/github_webhook.json") as f:
    instance.trigger( type="github_webhook", data=f.read().decode("utf-8") )

