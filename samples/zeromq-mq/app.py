#!/usr/bin/env python3

import json
import zmq
import zmq.asyncio
import asyncio

import sys
import time
import logging


logging.basicConfig(level=logging.DEBUG)

class ZMQ:
    config_data = {"url": "tcp://127.0.0.1:5690"}
    bind = False
    connect = False
    def __init__(self):
        #self.context = zmq.Context()
        self.context = zmq.asyncio.Context()
        self.sock = self.context.socket(self.socket_type)
        logging.debug(f"binding to {self.config_data['url']}")
        if self.bind == True:
            self.sock.bind(self.config_data['url'])
        elif self.connect == True:
            self.sock.connect(self.config_data['url'])

class Publisher(ZMQ):
    #socket_type = zmq.PUB
    socket_type = zmq.PUSH
    bind = True
    async def publish(self, queue="fooqueue", **kwargs):
        queuedict = {"queue": queue}
        newdict = {**queuedict, **kwargs}
        bytesobj = json.dumps(newdict).encode()
        #while True:
        future = await self.sock.send(bytesobj)
        logging.debug(f"sent {bytesobj} got future {future}")
        #task = asyncio.ensure_future(future)
        #logging.debug(f"task {task}")
        await asyncio.sleep(1)

class Subscriber(ZMQ):
    #socket_type = zmq.SUB
    socket_type = zmq.PULL
    connect = True
    async def subscribe(self):
        ## Subscribe to zipcode, default is NYC, 10001
        #topicfilter = "10001"
        #socket.setsockopt(zmq.SUBSCRIBE, topicfilter)
        string = await self.sock.recv()
        logging.debug(f"got string \"{string}\"")


async def publish():
    pub = Publisher()
    await asyncio.sleep(4)
    await pub.publish(msg="This is the message")

async def subscribe():
    sub = Subscriber()
    await sub.subscribe()


async def main():
    if len(sys.argv) < 2:
        asyncio.create_task( publish() )
        asyncio.create_task( subscribe() )
    elif sys.argv[1] == "publish":
        await publish()
    elif sys.argv[1] == "subscribe":
        await subscribe()

    logging.debug(f"everything is backgrounded")

    while True:
        all_tasks = asyncio.all_tasks()
        #logging.debug(f"all_tasks {all_tasks}")
        #res = await asyncio.gather()
        #logging.debug(f"res {res}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())

