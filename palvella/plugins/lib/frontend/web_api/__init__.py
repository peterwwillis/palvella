
"""
The plugin for the FastAPI 'web_api' plugin. Depends on the FastAPI plugin.

This plugin implements a series of APIs to interact with Palvella.
"""

from palvella.lib.plugin import PluginDependency
from ..fastapi import FastAPIPlugin, APIRouter  # noqa: PLE402

PLUGIN_TYPE = "web_api"


class WebAPI(FastAPIPlugin, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the Web API endpoints plugin."""

    fastapi_dependency = PluginDependency(parentclass="Frontend", plugin_type="fastapi")
    depends_on = [ fastapi_dependency ]

    def __pre_plugins__(self):
        """Register API router and routes with the already-initialized FastAPI app."""

        fastapi = self.get_component(self.fastapi_dependency)
        self._logger.debug(f"fastapi {fastapi}")

        web_api = APIRouter()
        web_api.add_api_route('/hello', endpoint=self.hello, methods=["GET"])

        self._logger.debug("Including web_api router in FastAPI app")
        for obj in fastapi:
            obj.app.include_router(web_api)

    async def hello(self):
        """An endpoint to test FastAPI."""  # noqa
        return {"message": "Hello World from the web_api plugin"}
