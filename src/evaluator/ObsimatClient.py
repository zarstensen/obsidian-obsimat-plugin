from typing import *
import websockets
import json
import traceback


#
# The ObsimatClient class manages a connection and message parsing + encoding between an active obsimat plugin.
# The connection works based on 'modes', which act like message types.
# A mode is simply a string indicating what sort of data is sent as the payload.
# The payload is always a json object decoded into a python object.
#
# Each mode can have a handler registered, which is called with the received payload when a message of that mode is received.
# The handler also gets a reference of the current ObsimatClient, so it can use the sendResult and sendError messages,
# to communicate back to the obsimat plugin.
#
class ObsimatClient:
    def __init__(self):
        self.modes = {}
        self.connection = None

    # Connect to an obsimat plugin currently hosting on the local host at the given port.
    async def connect(self, port: int):
        self.connection = await websockets.connect(f"ws://localhost:{port}")

    # Register a message mode handler.
    def register_mode(self, mode: str, handler: Callable[[Any, Self], None]):
        self.modes[mode] = handler

    # Send the given json dumpable object back to the plugin.
    async def sendResult(self, result: Any):
        await self.connection.send("result|" + json.dumps(result))

    # Signal to the plugin an error has occured, and give the following error message to it.
    async def sendError(self, error: str):
        await self.connection.send("error|" + json.dumps({
            'message': error
        }))

    # Start the message loop, this is required to run, before any handlers will be called.
    async def run_message_loop(self):
        while True:
            message = await self.connection.recv()
            mode, payload = message.split("|", 1)

            if mode in self.modes:
                try:
                    await self.modes[mode](json.loads(payload), self)
                except Exception as e:
                    await self.sendError(str(e) + "\n" + traceback.format_exc())
            else:
                await self.sendError("Unknown mode: " + mode)

        
