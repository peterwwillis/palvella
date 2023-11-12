#!/usr/bin/env python3

import asyncio
from ponyans.lib import *

async def main():
    await Frontend.load_plugins()
    await Trigger.load_plugins()

    # Infinite loop to wait for tasks to die and finally exit ourselves.
    # Without this, final task (this function) will not exit sanely on signals.
    while True:
        all_tasks = asyncio.all_tasks()
        await asyncio.sleep(0.5)
        logging.debug("Tasks pending: '{}'".format(all_tasks))
        cur_task = asyncio.current_task()
        excl_cur_task = (all_tasks - {cur_task})
        if len(excl_cur_task) < 1:
            logging.debug("All tasks complete!")
            return
        res = await asyncio.gather(*excl_cur_task)


#instance = Instance()
#instance.config.load(file="foo.yaml")

#with open("samples/github_webhook.json") as f:
#    instance.trigger( type="github_webhook", data=f.read().decode("utf-8") )

if __name__ == "__main__":
    asyncio.run(main())
