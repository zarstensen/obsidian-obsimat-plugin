from sympy_client.ModeResponse import ModeResponse
from typing import Any

## Implements the ModeResponse interface for testing purposes.
class MockResponse(ModeResponse):
    
    def __init__(self):
        self.reset()

    # resets all received responses.
    def reset(self):
        self.__error = None
        self.__warn = None
        self.__result = None

    # check if an error occured.
    def hasError(self):
        return self.__error is not None
    
    # check if a warning occured.
    def hasWarn(self):
        return self.__warn is not None
    
    # check if a result was sent.
    def hasResult(self):
        return self.__result is not None

    # get error message, if present.
    def getErrorMsg(self):
        return self.__error

    # get warning message, if present.
    def getWarnMsg(self):
        return self.__warn
    
    # get result if present.
    # format is a dictionary with the keys:
    # result, status, metadata
    def getResult(self):
        return self.__result

    async def error(self, message):
        self.__error = message
        pass

    async def warn(self, message):
        self.__warn = message
        pass

    async def result(self, result: Any, status: str = 'success', metadata: dict = {}):
        self.__result = {
            "result": result,
            "status": status,
            "metadata": metadata
        }