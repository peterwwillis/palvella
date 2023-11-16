import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve

from app import app

asyncio.run(serve(app, Config()))

