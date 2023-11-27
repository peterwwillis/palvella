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

from palvella.lib.instance.frontend import Frontend


ASGI_SERVER_TYPE = os.environ.get("ASGI_SERVER_TYPE", "uvicorn")
TYPE = "fastapi"


class FastAPIPlugin(Frontend, class_type="plugin"):
    """
    The 'FastAPI' plugin class.

    Attributes:
        TYPE: The name of the type of this Frontend plugin.
    """
    TYPE = TYPE

    def __pre_plugins__(self):
        """Initialize the FastAPI app and web server before loading the plugins that use it."""
        self.app = FastAPI()
        #self.APP_ENTRY = "palvella.plugins.lib.frontend.fastapi:app"
        self.APP_ENTRY = self.app

        if ASGI_SERVER_TYPE == "hypercorn":
            self.start_hypercorn()
        elif ASGI_SERVER_TYPE == "uvicorn":
            self.start_uvicorn()
        else:
            raise OSError("Invalid value for 'ASGI_SERVER_TYPE'")

    def start_uvicorn(self):
        """Start the Uvicorn server pointing at this plugin's FastAPI app() instance."""
        import uvicorn  # noqa: PLC415
        config = uvicorn.Config(self.APP_ENTRY, port=8000, log_level="info")
        server = uvicorn.Server(config)
        asyncio.create_task(server.serve())

    def start_hypercorn(self):
        """Start the Hypercorn server pointing at this plugin's FastAPI app() instance."""
        import hypercorn  # noqa: PLC415
        from hypercorn.asyncio import serve as hyperserve  # noqa: PLC415
        config = hypercorn.config.Config()
        config.application_path = self.APP_ENTRY
        config.bind = "127.0.0.1:8000"
        config.loglevel = "INFO"
        asyncio.create_task(hyperserve(self.app, config))

