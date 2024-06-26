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
from dataclasses import dataclass

# These are later imported by other plugins
from fastapi import (APIRouter, FastAPI, Request,  # noqa: F401,PLW406,PLW611
                     Response)

from palvella.lib.instance.frontend import Frontend


ASGI_SERVER_TYPE = os.environ.get("ASGI_SERVER_TYPE", "uvicorn")
PLUGIN_TYPE = "fastapi"


class FastAPIPlugin(Frontend, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """The 'FastAPI' plugin class."""

    app = FastAPI()

    def __pre_plugins__(self):
        """Initialize the FastAPI app and web server before loading the plugins that use it."""
        # TODO FIXME: Had to move this to the class level because it wasn't getting found
        # when the dependent plugin wanted it. Maybe this means we should wait until this
        # plugin is done initializing before continuing with the dependent plugins?
        #self.app = FastAPI()
        #self.APP_ENTRY = "palvella.plugins.lib.frontend.fastapi:app"
        self.APP_ENTRY = self.app

        self.logger.info(f"{self}: starting fastapi web server")
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

    @staticmethod
    def get_header(request, key):
        """Return message header."""
        try:
            return request.headers.get(key)
        except KeyError:
            return JSONResponse('{"error": "Missing header: ' + key + '"}', status_code=400)

    @staticmethod
    async def fastapi_data(request):
        @dataclass
        class FastAPIData(FastAPI):
            _json = None
            def __init__(self, request):
                self._content_type = FastAPIPlugin.get_header(request, "content-type")
                self._request = request
            @property
            async def body(self):
                return await self._request.body()
            @property
            async def json(self):
                if self._json: return self._json
                if self._content_type == "application/json":
                    self._json = await request.json()
                    if self._json is None:
                        return JSONResponse({"error": "Request body must contain json"}, status_code=400)
                else:
                    raise Exception(f"error: content_type '{self._content_type}' not implemented")
                    return Response(status_code=500)
                return self._json
        dataobj = FastAPIData(request)
        return dataobj

