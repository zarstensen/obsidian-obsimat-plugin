from sympy import Expr
from abc import ABC, abstractmethod

from sympy import Function, Symbol, Expr

class FunctionDefinition(ABC):
    @abstractmethod
    def call(self, *args: Expr) -> Expr:
        pass
    
    @abstractmethod
    def get_body(self) -> Expr:
        return self.call(*self.args)


class DefinitionsStore(ABC):
    @abstractmethod
    def get_function_definition(self, function: Function) -> FunctionDefinition | None:
        pass
    
    def deserialize_function(self, serialized_function: str) -> Function:
        return Function(serialized_function)
    
    @abstractmethod
    def get_symbol_definition(self, symbol: Symbol) -> Expr | None:
        pass
    
    def deserialize_symbol(self, serialized_symbol: str) -> Symbol:
        return Symbol(serialized_symbol)

# Interface for classes implementing sympy parsing functionality in the context of an LmatEnvironment.
class SympyParser(ABC):
    @abstractmethod
    def parse(self, serialized: str, definitions_store: DefinitionsStore) -> Expr:
        pass
