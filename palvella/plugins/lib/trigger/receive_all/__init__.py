"""
The plugin for the Trigger 'receive_all'. Defines plugin class and some base functions.
"""

import asyncio

from palvella.lib.plugin import PluginDependency
from palvella.lib.instance.trigger import Trigger
from palvella.plugins.lib.frontend.fastapi import Request

PLUGIN_TYPE = "receive_all"


class ReceiveAllTriggers(Trigger, class_type="plugin", plugin_type=PLUGIN_TYPE):
    """Class of the Receive All Triggers trigger."""

    def __pre_plugins__(self):
        self.logger.debug("Running receive_events()")
        asyncio.create_task( self.receive_events() )

    async def receive_events(self):
        while True:
            await asyncio.sleep(0.2)
            self.logger.debug(f"receive_events({self}): About to consume")
            gathered = await asyncio.gather( self.consume() )

            msg_objs = gathered[0]
            for arg in msg_objs:
                self.logger.debug(f"got msg_objs {arg}")
            #if msg_obj # TODO: FINISH ME
            await self.trigger(*msg_objs)

