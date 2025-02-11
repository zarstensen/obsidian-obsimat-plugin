from ClientBase import ClientBase
from typing import Any

class TestClient(ClientBase):
    
    def __init__(self):
        self.response = None
        self.sympy_response = None
        self.response_mode = None
    
    def hasResponse(self) -> bool:
        return self.response is not None
    
    def hasSympyResponse(self) -> bool:
        return self.sympy_response is not None
    
    def getResponseMode(self) -> str:
        return self.response_mode
    
    def getResponse(self) -> dict:
        return self.response
    
    def getSympyResponse(self) -> Any:
        return self.sympy_response
    
    def isError(self) -> bool:
        return self.response_mode == 'error'
    
    # Send the given json dumpable object back to the plugin.
    async def sendResult(self, result: Any):
        self.response = result
        self.response_mode = 'result'
        pass
    
        # Send the given json dumpable object back to the plugin.
    async def sendSympyResult(self, result: Any, metadata: dict):
        self.sympy_response = result
        self.response = metadata
        self.response_mode = 'result'
        pass

    async def sendError(self, error: str):
        self.response = { 'message': error}
        self.response_mode = 'error'