#!/usr/bin/env python3

import asyncio

from palvella.lib import Instance, logging


async def main():

    inst = Instance( config = "foo.yaml" )
    await inst.initialize()
    logging.debug("done loading instance")

    # Infinite loop to wait for tasks to die and finally exit ourselves.
    # Without this, final task (this function) will not exit sanely on signals.
    while True:
        all_tasks = asyncio.all_tasks()
        logging.debug("Tasks pending: '{}'".format(all_tasks))
        await asyncio.sleep(0.5)

        cur_task = asyncio.current_task()
        excl_cur_task = (all_tasks - {cur_task})
        if len(excl_cur_task) < 1:
            logging.debug("All tasks complete!")
            return
        res = await asyncio.gather(*excl_cur_task)


#with open("samples/github_webhook.json") as f:
#    instance.trigger( type="github_webhook", data=f.read().decode("utf-8") )

if __name__ == "__main__":
    asyncio.run(main())
