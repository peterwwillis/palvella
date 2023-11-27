
"""
The plugin for the FastAPI 'web_api' plugin. Depends on the FastAPI plugin.

This plugin implements a series of APIs to interact with Palvella.
"""

from palvella.lib.logging import logging

from ..fastapi import FastAPIPlugin, APIRouter  # noqa: PLE402

TYPE = "web_api"


class WebAPI(FastAPIPlugin, class_type="plugin"):
    """
    Class of the Web API endpoints plugin.

    Attributes of this class:
        'TYPE'      - The name of the type of this plugin.
    """

    TYPE = TYPE

    def __pre_plugins__(self):
        """Register API router and routes with the already-initialized FastAPI app."""
        web_api = APIRouter()
        web_api.add_api_route('/hello', endpoint=self.hello, methods=["GET"])
        logging.debug("Including web_api router in FastAPI app")
        self.parent.app.include_router(web_api)

    async def hello(self):
        """An endpoint to test FastAPI."""  # noqa
        return {"message": "Hello World from the web_api plugin"}
