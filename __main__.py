
from lib.job import *

#dockerengine = Engine(
#
#)

tfjob = Job(
    name    =   "Terraform job",
    args    =   {
                    "account":      "project1",
                    "environment":  "nonprod"
                },
    actions =   [
                    Action()
                ]
)
