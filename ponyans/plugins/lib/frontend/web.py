import asyncio
import subprocess

from .fastapi import FastAPI, APIRouter, app

import pywebio
from pywebio.input import *
from pywebio.output import *
from pywebio.platform.fastapi import webio_routes

async def main():
    pywebio.session.set_env(title='Awesome PyWebIO!!', output_animation=False)
    while True:
        with use_scope('result', clear=True):
            info = await input_group("App to run",
                [
                    input("Command to run", name='command')
                ]
            )
            put_markdown( "*Command:* `" + info['command'] + "`", sanitize=True )
            result = subprocess.run(
                info['command'],
                input=None, text=True, check=False, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            put_text("Output:\n")
            put_scrollable( put_code(result.stdout), keep_bottom=True )
            await actions(buttons=["Continue"])
            #pywebio.output.clear()

app.mount("/", FastAPI(routes=webio_routes(main)))

