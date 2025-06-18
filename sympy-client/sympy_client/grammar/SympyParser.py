from abc import ABC, abstractmethod

from sympy import Expr, Function, Symbol


# Interface class for a function definition in a DefinitionStore.
# It holds both its original serialized body and a deserialized version.
# Also provides an interface for,
# invoking a serialized version of its body with passed arguments.
class FunctionDefinition(ABC):
    @abstractmethod
    def call(self, *args: Expr) -> Expr:
        pass

    @abstractmethod
    def get_body(self) -> Expr:
        pass

    @property
    @abstractmethod
    def args(self) -> tuple[Expr]:
        pass

    @property
    @abstractmethod
    def serialized_body(self) -> str:
        pass

# Interface for classes storing a list of sympy symbol and function definitions.
class DefinitionStore(ABC):
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

# Interface for classes implementing sympy parsing functionality in the context of a DefinitionsStore.
class SympyParser(ABC):
    @abstractmethod
    def parse(self, serialized: str, definitions_store: DefinitionStore) -> Expr:
        pass
