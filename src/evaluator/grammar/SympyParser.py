from abc import ABC, abstractmethod
from ObsimatEnvironment import ObsimatEnvironment

# Interface for classes implementing sympy parsing functionality in the context of an ObsimatEnvironment.
class SympyParser:
    @abstractmethod
    def doparse(self, serialized: str, environment: ObsimatEnvironment):
        pass
