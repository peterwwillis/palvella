
"""
The plugin for the Frontend 'fastapi'. Defines plugin class and some base functions.

Other frontend plugins that want to use a FastAPI server will import this plugin.
They can also import FastAPI methods from this module, and particularly the 'app'
FastAPI() object instance.

After all plugins are loaded, Palvella will run the 'plugin_init' function in
this plugin, which will start the Uvicorn server.
"""

import asyncio
import os

# These are later imported by other plugins
from fastapi import (APIRouter, FastAPI, Request,  # noqa: F401,PLW406,PLW611
                     Response)

app = FastAPI()
APP_ENTRY = "palvella.plugins.lib.frontend.fastapi:app"
ASGI_SERVER_TYPE = os.environ.get("ASGI_SERVER_TYPE", "uvicorn")


async def start_uvicorn():
    """Start the Uvicorn server pointing at this plugin's FastAPI app() instance."""
    import uvicorn  # noqa: PLC415
    config = uvicorn.Config(APP_ENTRY, port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())


async def start_hypercorn():
    """Start the Hypercorn server pointing at this plugin's FastAPI app() instance."""
    import hypercorn  # noqa: PLC415
    from hypercorn.asyncio import serve as hyperserve  # noqa: PLC415
    config = hypercorn.config.Config()
    config.application_path = APP_ENTRY
    config.bind = "127.0.0.1:8000"
    config.loglevel = "INFO"
    asyncio.create_task(hyperserve(app, config))


async def instance_init(**kwargs):
    """Run the web server after all Palvalla plugins have been imported."""
    if ASGI_SERVER_TYPE == "hypercorn":
        await start_hypercorn()
    elif ASGI_SERVER_TYPE == "uvicorn":
        await start_uvicorn()
    else:
        raise OSError("Invalid value for 'ASGI_SERVER_TYPE'")
