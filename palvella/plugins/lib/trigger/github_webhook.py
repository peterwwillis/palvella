# Parts of this module taken from https://github.com/bloomberg/python-github-webhook/tree/master
# due to that module being written for Flask.
# That code is licensed here: https://github.com/bloomberg/python-github-webhook/blob/master/LICENSE

import six
import hmac
from typing import Any

from starlette.responses import HTMLResponse, JSONResponse

from palvella.plugins.lib.frontend.fastapi import FastAPI, Request, Response, app

from palvella.lib.logging import logging as logging
from palvella.lib.trigger import Trigger

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

    async def get_digest(self, request):
        """Return message digest if a secret key was provided"""
        return hmac.new(self._secret, request.data, hashlib.sha1).hexdigest() if self._secret else None

    @staticmethod
    def get_header(request, key):
        """Return message header"""
        logging.debug("headers: '{}'".format(request.headers))
        try:
            return request.headers.get(key)
        except KeyError:
            JSONResponse('{"error": "Missing header: ' + key + '"}', status_code=400)

    #def __init__(self, **extra: Any):
    #    super().__init__(**extra)
    #    #self.add_api_route("/", self.get_root, methods=["GET"], include_in_schema=False)
    #    #self.add_api_route("/version", self.get_version, methods=["GET"])

    async def github_webhook(self, request: Request):
        digest = self.get_digest(request)
        if digest is not None:
            foo = self.get_header(request, "X-Hub-Signature")
            logging.debug("foo: '{}'".format(foo))
            sig_parts = foo.split("=", 1)
            if not isinstance(digest, six.text_type):
                digest = six.text_type(digest)
            if len(sig_parts) < 2 or sig_parts[0] != "sha1" or not hmac.compare_digest(sig_parts[1], digest):
                return JSONResponse({"error": "Invalid signature"}, status_code=400)

        event_type = self.get_header(request, "X-Github-Event")
        content_type = self.get_header(request, "content-type")
        data = (
            json.loads(request.form.to_dict(flat=True)["payload"])
            if content_type == "application/x-www-form-urlencoded"
            else request.get_json()
        )
        if data is None:
            return JSONResponse({"error": "Request body must contain json"}, status_code=400)
        self._logger.info("%s (%s)", _format_event(event_type, data), self.get_header(request, "X-Github-Delivery"))
        # TODO: implement me
        #for hook in self._hooks.get(event_type, []):
        #    hook(data)
        return JSONResponse("", status_code=204)


webhook = GitHub_Webhook() # Defines '/postreceive' endpoint

async def plugin_init():
    app.add_api_route("/github_webhook", webhook.github_webhook, methods=["POST"])

