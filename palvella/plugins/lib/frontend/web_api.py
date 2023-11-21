
"""
The plugin for the Frontend 'web_api'. Defines plugin class and some base functions.

This plugin implements a series of APIs to interact with Palvella.
"""

from palvella.lib.logging import logging

from .fastapi import APIRouter, app  # noqa: PLE402

web_api = APIRouter()


@web_api.get("/hello")
async def hello():
    """An endpoint to test FastAPI."""  # noqa
    return {"message": "Hello World from the web_api plugin"}


async def instance_init(**kwargs):
    """Add a router to this web API to the FastAPI app."""
    logging.debug("Including web_api router in FastAPI app")
    app.include_router(web_api)
