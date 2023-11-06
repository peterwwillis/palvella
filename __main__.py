
from lib.job import Job
from lib.action import Action
from lib.engine import Engine

#import importlib
#import pkgutil
#import myapp.plugins

#def iter_namespace(ns_pkg):
#    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")
#discovered_plugins = {
#    name: importlib.import_module(name)
#    for finder, name, ispkg
#    in iter_namespace(myapp.plugins)
#}
#print("discovered: %s" % discovered_plugins)


localengine = Engine(
    name    = "local",
    type    = "local"
)


tfjob = Job(
    name    =   "Terraform job",
    engine  =   "docker",
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
                    Action(
                        name="Terraform Plan",
                        type="run",
                    )
                ]
)

