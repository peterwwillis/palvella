
"""
The plugin for the Frontend 'fastapi'. Defines plugin class and some base functions.

Other frontend plugins that want to use a FastAPI server will import this plugin.
They can also import FastAPI methods from this module, and particularly the 'app'
FastAPI() object instance.

After all plugins are loaded, Palvella will run the 'plugin_init' function in
this plugin, which will start the Uvicorn server.
"""

import os
import asyncio

# These are later imported by other plugins
from fastapi import (APIRouter, FastAPI, Request,  # noqa: F401,PLW406,PLW611
                     Response)

app = FastAPI()
app_entrypoint = "palvella.plugins.lib.frontend.fastapi:app"

web_server = os.environ.get("ASGI_SERVER_TYPE", "uvicorn")

async def start_uvicorn():
    """Start the Uvicorn server pointing at this plugin's FastAPI app() instance."""

    import uvicorn
    config = uvicorn.Config(app_entrypoint, port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())

async def start_hypercorn():
    import hypercorn
    from hypercorn.asyncio import serve as hypercornServe
    config = hypercorn.config.Config()
    config.application_path=app_entrypoint
    config.bind="127.0.0.1:8000"
    config.loglevel="INFO"
    asyncio.create_task(hypercornServe(app, config))

async def plugin_init():
    """Run the web server after all Palvalla plugins have been imported."""
    if web_server == "hypercorn":
        await start_hypercorn()
    elif web_server == "uvicorn":
        await start_uvicorn()
    else:
        raise Exception("please define 'web_server'")
