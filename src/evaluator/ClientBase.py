from abc import ABC, abstractmethod
from typing import Any

class ClientBase(ABC):
    @abstractmethod
    # Send the given json dumpable object back to the plugin.
    async def sendSympyResult(self, sympy_result: Any, metadata: dict = {}):
        pass

    @abstractmethod
    async def sendResult(self, result: Any):
        pass

    @abstractmethod
    async def sendError(self, error: str):
        pass
