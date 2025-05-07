from sympy import Expr
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from abc import ABC, abstractmethod

# Interface for classes implementing sympy parsing functionality in the context of an ObsimatEnvironment.
class SympyParser(ABC):
    @abstractmethod
    def doparse(self, serialized: str, environment: ObsimatEnvironment) -> Expr:
        pass
