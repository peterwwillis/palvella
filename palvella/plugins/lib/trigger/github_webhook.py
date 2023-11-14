# Parts of this module taken from https://github.com/bloomberg/python-github-webhook/tree/master
# due to that module being written for Flask.
# That code is licensed here: https://github.com/bloomberg/python-github-webhook/blob/master/LICENSE

import hmac
import json
import hashlib
# from typing import Any

from starlette.responses import JSONResponse

from palvella.plugins.lib.frontend.fastapi import Request, app

from palvella.lib.logging import logging
from palvella.lib.trigger import Trigger

type = "github_webhook"


class GitHub_Webhook(Trigger):
    """ Class of the GitHub Webhook trigger.
        Inherits the Trigger class.
    """

    _secret = None
    type = type

    def __init__(self, **kwargs):
        """ When creating a new object, pass arbitrary key=value pairs to update the object.
        """
        super().__init__(**kwargs)
        logging.debug(f"GitHub_Webhook({kwargs})")
        self.__dict__.update(kwargs)

    async def get_digest(self, request):
        """Return message digest if a secret key was provided"""
        if self._secret:
            return hmac.new(self._secret, request.data, hashlib.sha1).hexdigest()
        return None

    @staticmethod
    def get_header(request, key):
        """Return message header"""
        logging.debug(f"headers: '{request.headers}'")
        try:
            return request.headers.get(key)
        except KeyError:
            return JSONResponse('{"error": "Missing header: ' + key + '"}', status_code=400)

#    def __init__(self, **extra: Any):
#        super().__init__(**extra)
#        #self.add_api_route("/", self.get_root, methods=["GET"], include_in_schema=False)
#        #self.add_api_route("/version", self.get_version, methods=["GET"])

    async def github_webhook(self, request: Request):
        digest = await self.get_digest(request)
        if digest is not None:
            sig = self.get_header(request, "X-Hub-Signature")
            logging.debug(f"sig: '{sig}'")
            sig_parts = sig.split("=", 1)
            logging.debug(f"sig_parts '{sig_parts}' digest '{digest}'")
            if len(sig_parts) < 2 or sig_parts[0] != "sha1" \
               or not hmac.compare_digest(sig_parts[1], digest):
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
        logging.info("%s (%s)", (event_type+":"+data),
                     self.get_header(request, "X-Github-Delivery"))
#        # TODO: implement me
#        for hook in self._hooks.get(event_type, []):
#            hook(data)
        return JSONResponse("", status_code=204)


webhook = GitHub_Webhook()  # Defines '/postreceive' endpoint


async def plugin_init():
    app.add_api_route("/github_webhook", webhook.github_webhook, methods=["POST"])
