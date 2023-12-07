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
        asyncio.create_task( self.receive_events() )

    async def receive_events(self):
        while True:
            self._logger.debug(f"\nAbout to consume\n")
            consume_res = await self.consume()
            gathered = asyncio.gather(consume_res)
            self._logger.debug(f"ReceiveAllTriggers.receive_events: got {gathered}")
            await asyncio.sleep(1)
