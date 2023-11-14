import asyncio

from palvella.lib.logging import logging
from .fastapi import APIRouter, app

web_api = APIRouter()


@web_api.get("/foo")
async def foo():
    return {"message": "Hello World from main app"}


async def plugin_init():
    logging.debug("Including web_api router in FastAPI app")
    app.include_router(web_api)
