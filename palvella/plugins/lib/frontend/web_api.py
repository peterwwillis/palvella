
"""
The plugin for the Frontend 'web_api'. Defines plugin class and some base functions.

This plugin implements a series of APIs to interact with Palvella.
"""

from palvella.lib.logging import logging

from .fastapi import APIRouter, app  # noqa: PLE402
from palvella.lib.instance.frontend import Frontend

web_api = APIRouter()
TYPE = "web_api"


class WebAPI(Frontend):
    """
    Class of the Web API endpoints plugin.

    Attributes of this class:
        'TYPE'      - The name of the type of this plugin.
    """

    TYPE = TYPE

    @web_api.get("/hello")
    async def hello(self):
        """An endpoint to test FastAPI."""  # noqa
        return {"message": "Hello World from the web_api plugin"}

    @classmethod
    async def instance_init(cls, **kwargs):
        """Add a router to this web API to the FastAPI app."""
        logging.debug("Including web_api router in FastAPI app")
        app.include_router(web_api)
