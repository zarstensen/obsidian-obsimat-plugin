from abc import ABC, abstractmethod
from typing import Any, override


# The CommandResult represents an arbitrary result returned by a CommandHandler.
# It contains the result data and a method for converting this data into a message payload.
class CommandResult(ABC):

    @abstractmethod
    def getPayload(self) -> dict:
        pass

    # helper method for producing a common result payload.
    @staticmethod
    def result(result, metadata: dict = None, status: str = 'success') -> dict:
        return dict(result=result, metadata=metadata or {}, status=status)

class ErrorResult(CommandResult):

    def __init__(self, err_msg: str):
        super().__init__()
        self.err_msg = err_msg

    @override
    def getPayload(self) -> dict:
        return CommandResult.result(dict(message=self.err_msg), status='error')

# CommandHandler should be inherited by objects wanting to implement a handler.
# The handle method returns a CommandResult for the implemented command.
class CommandHandler(ABC):
    @abstractmethod
    def handle(self, message: Any) -> CommandResult:
        pass
