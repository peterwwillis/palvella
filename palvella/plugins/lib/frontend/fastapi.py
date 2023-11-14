
import asyncio

import uvicorn
# These are later imported by other plugins
from fastapi import APIRouter, FastAPI, Request, Response  # noqa: F401

app = FastAPI()


async def main():
    config = uvicorn.Config("palvella.plugins.lib.frontend.fastapi:app",
                            port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())


async def plugin_init():
    await main()
#    asyncio.create_task(main())
