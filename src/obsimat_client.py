from websockets.asyncio.client import ClientConnection
from sympy import *
from sympy import sympify
from sympy.parsing.latex import parse_latex, parse_latex_lark
from sympy.solvers.solveset import NonlinearError
import asyncio
import websockets
import sys

class ObsimatClient:
    def __init__(self):
        self.modes = {}
    
    async def connect(self, port: int):
        self.connection = await websockets.connect(f"ws://localhost:{port}")
    
    def register_mode(self, mode: str, handler):
        self.modes[mode] = handler
    
    async def run_message_loop(self):
        while True:
            message = await self.connection.recv()
            mode, payload = message.split("|", 1)
            
            if mode in self.modes:    
                try:
                    await self.modes[mode](payload, self)
                except Exception as e:
                    await self.sendError(str(e))
            else:
                await self.sendError("Unknown mode: " + mode)
                
                
    async def sendResult(self, result: str):
        await self.connection.send("result|" + result)
        
    async def sendError(self, error: str):
        await self.connection.send("error|" + error)
        
    
        
    