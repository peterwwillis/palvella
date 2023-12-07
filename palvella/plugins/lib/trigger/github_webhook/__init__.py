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

from palvella.lib.plugin import PluginDependency
from palvella.lib.instance.trigger import Trigger
from palvella.plugins.lib.frontend.fastapi import Request

PLUGIN_TYPE = "github_webhook"


class GitHubWebhook(Trigger, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the GitHub Webhook trigger. Inherits the Trigger class."""

    _secret = None

    fastapi_dependency = PluginDependency(parentclass="Frontend", plugin_type="fastapi")
    depends_on = [ fastapi_dependency ]

    def __pre_plugins__(self):
        """
        Add a route for the '/github_webhook' endpoint to the FastAPI plugin's web server.

        This method is called by the main app during Instance().initialize() after it creates
        a new object (of this class). Maps the HTTP endpoint in FastAPI to serve this function.
        """

        fastapi = self.get_component(self.fastapi_dependency)
        #self._logger.debug(f"fastapi {fastapi}")

        # TODO: For each configured webhook, create a new instance with its
        #       own configuration (endpoint name, secret, repo, etc)
        for obj in fastapi:
            obj.app.add_api_route("/github_webhook", self.github_webhook, methods=["POST"])
        #self._logger.debug("Done webhook install")

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

    async def github_webhook(self, request: Request):
        """FastAPI route to handle /github_webhook endpoint."""  # noqa

        sig = self.get_header(request, "X-Hub-Signature")
        hook_id = self.get_header(request, "X-Github-Hook-Id")
        delivery = self.get_header(request, "X-Github-Delivery")
        event_type = self.get_header(request, "X-Github-Event")
        content_type = self.get_header(request, "content-type")

        digest = await self.get_digest(request)
        if digest is not None:
            self._logger.debug(f"sig: '{sig}'")
            sig_parts = sig.split("=", 1)
            self._logger.debug(f"sig_parts '{sig_parts}' digest '{digest}'")
            if len(sig_parts) < 2 or sig_parts[0] != "sha1" \
               or not hmac.compare_digest(sig_parts[1], digest):
                self._logger.debug("github_webhook: invalid signature")
                return JSONResponse({"error": "Invalid signature"}, status_code=400)

        if content_type == "application/json":
            data = await request.json()
        else:
            self._logger.debug(f"github_webhook: error: content_type '{content_type}' not implemented")
            return Response(status_code=500)

        if data is None:
            return JSONResponse({"error": "Request body must contain json"}, status_code=400)

        self._logger.info(f"event_type:{event_type} data:{data} ({delivery})")

        # MessageQueue: Publish this message to the message queue as specified in
        #               the configuration for this webhook.
        await self.publish(
            event_type=event_type, hook_id=hook_id, delivery=delivery, data=data
        )

        # For 204 status code, you *MUST NOT* use a JSONResponse or HTTPResponse,
        # but only Response, with no body. Otherwise FastAPI will inject some junk
        # in the body that causes the h11 library to throw exceptions, because for
        # 204 there should be no body at all.
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
