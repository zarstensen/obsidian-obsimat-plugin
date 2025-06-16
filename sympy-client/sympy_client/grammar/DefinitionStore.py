# Interface for classes storing a list of sympy symbol and function definitions.

# Interface class for a function definition in a DefinitionStore.
# It holds both its original serialized body and a deserialized version.
# Also provides an interface for,
# invoking a serialized version of its body with passed arguments.
from abc import ABC, abstractmethod
from typing import Self

from lark import Tree
from sympy import Expr, Function, Symbol


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

class SymbolDefinition:

    def __init__(self, symbol, value, dependencies):
        self._symbol = symbol
        self._value = value
        self._dependencies = dependencies
    
    @property
    def symbol(self) -> Symbol:
        return self._symbol

    @property
    def dependencies(self) -> set[Self]:
        return self._symbol_dependencies
    
    @property
    def value(self) -> Expr:
        return self._value

class DefinitionStore(ABC):
    
    @abstractmethod
    def get_function_definition(self, function: Function) -> FunctionDefinition | None:
        pass
    
    def deserialize_function(self, serialized_function: str) -> Function:
        return Function(serialized_function)
    
    @abstractmethod
    def get_symbol_definition(self, symbol: Symbol) -> SymbolDefinition | None:
        pass
    
    def deserialize_symbol(self, serialized_symbol: str) -> Symbol:
        return Symbol(serialized_symbol)