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
from palvella.plugins.lib.frontend.fastapi import Request, FastAPIPlugin

PLUGIN_TYPE = "github_webhook"


class GitHubWebhook(Trigger, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the GitHub Webhook trigger. Inherits the Trigger class."""

    name = None
    secret = None

    fastapi_dependency = PluginDependency(parentclass="Frontend", plugin_type="fastapi")
    depends_on = [ fastapi_dependency ]

    def __pre_plugins__(self):
        """
        Add a route for the '/github_webhook' endpoint to the FastAPI plugin's web server.

        This method is called by the main app during Instance().initialize() after it creates
        a new object (of this class). Maps the HTTP endpoint in FastAPI to serve this function.
        """

        for x in ['name', 'secret']:
            if x in self.config_data:
                setattr(self, x, self.config_data[x])

        fastapi = self.get_component(self.fastapi_dependency)

        # TODO: For each configured webhook, create a new instance with its
        #       own configuration (endpoint name, secret, repo, etc)
        for obj in fastapi:
            self.logger.info(f"{self}: {obj.app}.add_api_route(\"/github_webhook\")")
            obj.app.add_api_route("/github_webhook", self.github_webhook, methods=["POST"])

    async def get_digest(self, data, hashfunc):
        """Return message digest if a secret key was provided."""
        if self.secret:
            hmacobj = hmac.new(self.secret.encode(), data, hashfunc)
            digest = hmacobj.hexdigest()
            return digest
        return None

    async def github_webhook(self, request: Request):
        """FastAPI route to handle /github_webhook endpoint."""  # noqa

        data = await FastAPIPlugin.fastapi_data(request)

        sig = FastAPIPlugin.get_header(request, "X-Hub-Signature-256")
        hook_id = FastAPIPlugin.get_header(request, "X-Github-Hook-Id")
        delivery = FastAPIPlugin.get_header(request, "X-Github-Delivery")
        event_type = FastAPIPlugin.get_header(request, "X-Github-Event")
        content_type = FastAPIPlugin.get_header(request, "content-type")

        self.logger.info(f"github_webhook(self={self}, request=(client={request.client}, method={request.method}, url.scheme={request.url.scheme}, url.port={request.url.port}, url.path='{request.url.path}'))")

        digest = await self.get_digest(await data.body, hashfunc=hashlib.sha256)
        if digest is not None:
            if not hmac.compare_digest(sig, digest):
                self.logger.error("github_webhook: invalid signature")
                return JSONResponse({"error": "Invalid signature"}, status_code=400)

        jsondata = await data.json
        await self.trigger(
            meta = {
              "mq":      { "event_type": "trigger" },
              "webhook": { "event_type": event_type,
                           "hook_id": hook_id,
                           "delivery": delivery }
            },
            data = [jsondata]
        )

        # For 204 status code, you *MUST NOT* use a JSONResponse or HTTPResponse,
        # but only Response, with no body. Otherwise FastAPI will inject some junk
        # in the body that causes the h11 library to throw exceptions, because for
        # 204 there should be no body at all.
        return Response(status_code=HTTPStatus.NO_CONTENT.value)
