# Parts of this module taken from https://github.com/bloomberg/python-github-webhook/tree/master
# due to that module being written for Flask.
# That code is licensed here: https://github.com/bloomberg/python-github-webhook/blob/master/LICENSE

"""
The plugin for the Trigger 'github_webhook'. Defines plugin class and some base functions.

This plugin registers a GitHub Webhook trigger '/github_webhook' using the FastAPI
web server plugin.
"""

import hashlib
import hmac
from http import HTTPStatus

from starlette.responses import JSONResponse, Response

from palvella.lib.logging import logging
from palvella.lib.trigger import Trigger
from palvella.plugins.lib.frontend.fastapi import Request, app

# from typing import Any


TYPE = "github_webhook"


class GitHubWebhook(Trigger):
    """Class of the GitHub Webhook trigger. Inherits the Trigger class."""

    _secret = None
    TYPE = TYPE

    async def get_digest(self, request):
        """Return message digest if a secret key was provided."""
        if self._secret:
            return hmac.new(self._secret, request.data, hashlib.sha1).hexdigest()
        return None

    @staticmethod
    def get_header(request, key):
        """Return message header."""
        try:
            return request.headers.get(key)
        except KeyError:
            return JSONResponse('{"error": "Missing header: ' + key + '"}', status_code=400)

#    def __init__(self, **extra: Any):
#        super().__init__(**extra)
#        #self.add_api_route("/", self.get_root, methods=["GET"], include_in_schema=False)
#        #self.add_api_route("/version", self.get_version, methods=["GET"])

    async def github_webhook(self, request: Request):
        """FastAPI route to handle /github_webhook endpoint."""  # noqa

        sig = self.get_header(request, "X-Hub-Signature")
        delivery = self.get_header(request, "X-Github-Delivery")
        event_type = self.get_header(request, "X-Github-Event")
        content_type = self.get_header(request, "content-type")

        digest = await self.get_digest(request)
        if digest is not None:
            logging.debug(f"sig: '{sig}'")
            sig_parts = sig.split("=", 1)
            logging.debug(f"sig_parts '{sig_parts}' digest '{digest}'")
            if len(sig_parts) < 2 or sig_parts[0] != "sha1" \
               or not hmac.compare_digest(sig_parts[1], digest):
                return JSONResponse({"error": "Invalid signature"}, status_code=400)

        if content_type == "application/x-www-form-urlencoded":  # noqa: PLR720
            form = await request.form()
            for k, v in form.multi_items():
                logging.debug(f"k '{k}' v '{v}'")
            # TODO: FIXME: this is broken; forms aren't coming back right!  # noqa
            raise NotImplementedError
            # data = json.loads(form.foobar)
        elif content_type == "application/json":
            data = await request.json()

        if data is None:
            return JSONResponse({"error": "Request body must contain json"}, status_code=400)

        logging.info(f"event_type:{event_type} data:{data} ({delivery})")

#        # TODO: implement me  # noqa
#        for hook in self._hooks.get(event_type, []):
#            hook(data)
        # For 204 status code, you *MUST NOT* use a JSONResponse or HTTPResponse,
        # but only Response, with no body. Otherwise FastAPI will inject some junk
        # in the body that causes the h11 library to throw exceptions, because for
        # 204 there should be no body at all.
        return Response(status_code=HTTPStatus.NO_CONTENT.value)


webhook = GitHubWebhook()  # Defines '/postreceive' endpoint


async def plugin_init():
    """Add a route for the '/github_webhook' endpoint to the FastAPI plugin's web server."""
    app.add_api_route("/github_webhook", webhook.github_webhook, methods=["POST"])
