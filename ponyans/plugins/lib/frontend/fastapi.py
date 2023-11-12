
import asyncio
import uvicorn

import fastapi
from fastapi import * # FastAPI, APIRouter

app = FastAPI()

async def main():
    config = uvicorn.Config("ponyans.plugins.lib.frontend.fastapi:app", port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task( server.serve() )

async def plugin_init():
    await main()
    #asyncio.create_task(main())

