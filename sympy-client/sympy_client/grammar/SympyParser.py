from sympy import Expr
from sympy_client.LmatEnvironment import LmatEnvironment
from abc import ABC, abstractmethod

# Interface for classes implementing sympy parsing functionality in the context of an LmatEnvironment.
class SympyParser(ABC):
    @abstractmethod
    def doparse(self, serialized: str, environment: LmatEnvironment) -> Expr:
        pass
