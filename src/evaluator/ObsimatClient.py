from ModeResponse import ModeResponse

from typing import *
import websockets
import json
import traceback
import re

from grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy import latex, evaluate


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
    def __init__(self, latex_parser: ObsimatLatexParser):
        self.modes = {}
        self.connection = None
        self.__latex_parser = latex_parser

    # Connect to an obsimat plugin currently hosting on the local host at the given port.
    async def connect(self, port: int):
        self.connection = await websockets.connect(f"ws://localhost:{port}")

    # Register a message mode handler.
    def register_mode(self, mode: str, handler: Callable[[Any, ModeResponse, ObsimatLatexParser], None], formatter: Callable[[Any, str, dict], str] = None):
        self.modes[mode] = {
            'handler': handler,
            'formatter': formatter or ObsimatClient.__default_sympy_formatter
        }
    
    # Send the given json dumpable object back to the plugin.
    async def send(self, mode: str, message: dict):
        await self.connection.send(f"{mode}|{json.dumps(message)}")

    # Signal to the plugin an error has occured, and give the following error message to it.

    # Start the message loop, this is required to run, before any handlers will be called.
    async def run_message_loop(self):
        while True:
            message = await self.connection.recv()
            mode, payload = message.split("|", 1)

            
            if mode in self.modes:
                response = ObsimatClient.ObsimatClientResponse(self, self.modes[mode]['formatter'])
                try:
                    loaded_payload = json.loads(payload)
                    self.__latex_parser.set_environment(loaded_payload['environment'])
                    await self.modes[mode]['handler'](loaded_payload, response, self.__latex_parser)
                except Exception as e:
                    await response.error(str(e) + "\n" + traceback.format_exc())
            else:
                await self.send("error", { 'message':  mode })
    
    # The default formatter used to conver the results of a mode handler,
    # into a displayable string.
    # simply converts the given expression to latex, and remove any text formatting.
    @staticmethod
    def __default_sympy_formatter(sympy_expr: Any, _status: str, _metadata: dict) -> str:
        return re.sub(r"\\text\{(.*?)\}", r"\1", latex(sympy_expr))
    
    # The ObsimatClientResponse class is a helper class for the ObsimatClient,
    # which implements the ModeResponse interface and sends the responses to the obsimat plugin via. the ObsimatClient.
    class ObsimatClientResponse(ModeResponse):
        def __init__(self, client: Self, formatter: Callable[[Any, str, dict], str]):
            self.client = client
            self.formatter = formatter

        async def error(self, message):
            await self.client.send('error', { 'message': message })

        async def warn(self, message):
            await self.client.send('warn', { 'message': message })

        async def result(self, result: Any, status: str = 'success', metadata: dict[str, str] = {}):
            # Sympy sometimes errors out when trying to convert a sympy expression to a string,
            # when evaluate is set to false, so here it is forced to always be true.
            with evaluate(True):
                await self.client.send('result', { 'result': self.formatter(result, status, metadata), 'status': status, 'metadata': metadata })

        
