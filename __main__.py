
from lib.job import *

tfjob = Job(
    name    =   "Terraform job",
    args    =   {
                    "account":      "project1",
                    "environment":  "nonprod"
                },
    actions =   [
                    
                ]
)
