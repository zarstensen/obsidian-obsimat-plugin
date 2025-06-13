import asyncio
from threading import Thread
import traceback
from typing import *

import jsonpickle
import websockets

from .command_handlers.CommandHandler import CommandHandler


#
# The LatexMathClient class manages a connection and message parsing + encoding between an active Latex Math plugin.
# The connection works based on 'handle keys', which act like message types.
# A handle key is simply a string indicating what sort of data is sent as the payload, and how it should be handled.
# The payload is always a json object decoded into a python object.
#
# Each handle key has a handler registered, which is called with the received payload.
#
class LatexMathClient:
    def __init__(self):
        self.handlers: dict[str, CommandHandler] = { }
        self.handler_threads: dict[str, Thread] = { }
        self.connection = None

    # Connect to a Latex Math plugin currently hosting on the local host at the given port.
    async def connect(self, port: int):
        self.connection = await websockets.connect(f"ws://localhost:{port}")

    # Register a message handler.
    def register_handler(self, handler_key: str, handler_factory: CommandHandler):
        self.handlers[handler_key] = handler_factory

    # Send the given json dumpable object back to the plugin.
    async def send(self, status: str, uid: str, message: dict):
        await self.connection.send(jsonpickle.encode(dict(status=status, uid=uid, response=message)))

    # Start the message loop, this is required to run, before any handlers will be called.
    async def run_message_loop(self):
        while True:
            message = jsonpickle.decode(await self.connection.recv())
            uid = message['uid']

            match message.type:
                case "exit":
                    await self.send("exit", uid, {})
                    break
                case "start":
                    if message['command'] not in self.handlers:
                        await self.send('error', uid, dict(message=message['command']))
                    
                    # TODO: this should be a thread
                    try:
                        self.handler_threads[uid] = Thread(target=asyncio.run, args=(self.handleAndRespond(message['command'], uid, message['payload']),))
                        self.handler_threads[uid].start()
                    except Exception as e:
                        await self.send('error', uid, dict(message=str(e) + "\n" + traceback.format_exc()))
                            
                    break
                case _:
                    # unknown type, idk return an error or whatever, probably a custom thing.
                    break
    
    async def handleAndRespond(self, command: str, uid: str, payload: dict):
        command_result = self.handlers[command].handle(payload)
        await self.send('result', uid, command_result.getPayload())