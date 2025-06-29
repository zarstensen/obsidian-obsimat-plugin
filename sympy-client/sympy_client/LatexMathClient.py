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
        self.handlers: dict[str, CommandHandler] = {}
        self.connection = None

    # Connect to a Latex Math plugin currently hosting on the local host at the given port.
    async def connect(self, port: int):
        self.connection = await websockets.connect(f"ws://localhost:{port}")

    # Register a message handler.
    def register_handler(self, handler_key: str, handler_factory: CommandHandler):
        self.handlers[handler_key] = handler_factory

    # Send the given json dumpable object back to the plugin.
    async def send(self, handler_key: str, message: dict):
        await self.connection.send(f"{handler_key}|{jsonpickle.encode(message)}")

    # Start the message loop, this is required to run, before any handlers will be called.
    async def run_message_loop(self):
        while True:
            message = await self.connection.recv()
            handler_key, payload = message.split("|", 1)

            if handler_key == "exit":
                await self.send("exit", {})
                break

            if handler_key in self.handlers:
                try:
                    loaded_payload = jsonpickle.decode(payload)
                    command_result = self.handlers[handler_key].handle(loaded_payload)
                    await self.send('result', command_result.getPayload())
                except Exception as e:
                    await self.send("error", dict(message=str(e) + "\n" + traceback.format_exc()))
            else:
                await self.send("error", dict(message=f"Unsupported command: {handler_key}"))
