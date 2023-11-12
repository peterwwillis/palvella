import asyncio
import subprocess

from .fastapi import APIRouter, app

web_api = APIRouter()

@web_api.get("/foo")
async def foo():
   return {"message": "Hello World from main app"}

app.include_router(web_api)
