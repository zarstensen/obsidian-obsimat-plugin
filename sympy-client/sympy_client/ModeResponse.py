from abc import ABC, abstractmethod
from typing import Any

# Interface for mode handlers to communicate a response back to their caller.
class ModeResponse(ABC):

    # Indicate an error has occured,
    # with the given message as an error description.
    @abstractmethod
    async def error(self, message):
        pass

    # Indicate a warning has occured,
    # with the given message as a warning description.
    @abstractmethod
    async def warn(self, message):
        pass

    # Gives the following result back to the caller.
    @abstractmethod
    async def result(self, result: Any, status: str = 'success', metadata: dict[str, str] = {}):
        pass