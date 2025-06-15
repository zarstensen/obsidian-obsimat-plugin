from typing import Callable
from lark import Lark, Tree
from sympy import Expr
from abc import ABC, abstractmethod

from sympy import Function, Symbol, Expr

from sympy_client.grammar import DefinitionStore
from sympy_client.grammar.transformers.DefStoreBaseTransformer import DefStoreBaseTransformer


# Interface for classes implementing sympy parsing functionality in the context of a DefinitionsStore.
# XXX: What is the point of this?
#      should this not just be direct lark stuff?
#      is another parser ever going to be used, probably not?
#      if anything, it would be sympy which is replaced as the CAS, and not lark as the parser???
#      So, remove this, and just have the parser be a lark and a transformer pair it is easier to split up that way, since this needs to be done anyways.
#      there could be a series of helper methods which then pair up some common lark instances (only one for now?) and transformers.

class DefStoreLarkCompiler:
    
    def __init__(self, parser: Lark, transformer_cls: Callable[[], DefStoreBaseTransformer]):
        self._parser = parser
        self._transformer_cls = transformer_cls
    
    def compile(self, serialized: str, definition_store: DefinitionStore) -> Expr:
        return self._transformer_cls(definition_store).transform(self._parser.parse(serialized))
