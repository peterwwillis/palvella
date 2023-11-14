
"""
The plugin for the Frontend 'fastapi'. Defines plugin class and some base functions.

Other frontend plugins that want to use a FastAPI server will import this plugin.
They can also import FastAPI methods from this module, and particularly the 'app'
FastAPI() object instance.

After all plugins are loaded, Palvella will run the 'plugin_init' function in
this plugin, which will start the Uvicorn server.
"""

import asyncio

import uvicorn
# These are later imported by other plugins
from fastapi import (APIRouter, FastAPI, Request,  # noqa: F401,PLW406,PLW611
                     Response)

app = FastAPI()


async def main():
    """Start the Uvicorn server pointing at this plugin's FastAPI app() instance."""
    config = uvicorn.Config("palvella.plugins.lib.frontend.fastapi:app",
                            port=8000, log_level="info")
    server = uvicorn.Server(config)
    asyncio.create_task(server.serve())


async def plugin_init():
    """Run the Uvicorn server after all Palvalla plugins have been imported."""
    await main()
