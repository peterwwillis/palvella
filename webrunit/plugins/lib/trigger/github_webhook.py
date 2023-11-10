
from webrunit.lib.logging import logging as logging
from webrunit.lib.trigger.base import Trigger

type = "github_webhook"

class GitHub_Webhook(Trigger):
    """ Class of the GitHub Webhook trigger.
        Inherits the Trigger class.
    """

    type = type

    def __init__(self, **kwargs):
        """ When creating a new object, pass arbitrary key=value pairs to update the object.
        """
        logging.debug("GitHub_Webhook(%s)" % (kwargs))
        self.__dict__.update(kwargs)

classref = GitHub_Webhook
logging.debug("Loaded plugin github_webhook")
