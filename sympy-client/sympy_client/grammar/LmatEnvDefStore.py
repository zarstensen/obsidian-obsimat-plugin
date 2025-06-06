from copy import copy
from typing import Iterable

from sympy import Expr, Function, Symbol
from sympy_client.grammar.SympyParser import (DefinitionStore,
                                              FunctionDefinition, SympyParser)
from sympy_client.LmatEnvironment import LmatEnvironment


class LmatEnvFunctionDefinition(FunctionDefinition):
    def __init__(self, definition_store: DefinitionStore, parser: SympyParser, args: Iterable[Symbol], latex_expr: str):
        super().__init__()
        self._definitions_store = definition_store
        self._parser = parser
        self._args = tuple(args)
        self._latex_expr = latex_expr

    def call(self, *args) -> Expr:
        assert len(args) == len(self.args)

        args_map = { arg: val for arg, val in zip(self.args, args) }
        func_def_store = LmantEnvFuncDefStore(args_map, self._definitions_store)
        
        expr = self._parser.parse(self.serialized_body, func_def_store)
        
        return expr
    
    def get_body(self):
        return self.call(*self.args)
    
    @property
    def args(self) -> tuple[Expr]:
        return self._args
    
    @property
    def serialized_body(self) -> str:
        return self._latex_expr

# Definition store implementation in the context of an LmatEnvironment.
# provides definitions and deserializatiosn based on the symbols, variables and functions tables.
class LmatEnvDefStore(DefinitionStore):
    
    def __init__(self, parser: SympyParser, environment: LmatEnvironment):
        super().__init__()
        
        self._parser = parser
        
        self._environment = environment
        
        self._cached_symbols = {}
        self._cached_symbol_definitions = {}

        self._serialized_symbol_definitions = {
            self.deserialize_symbol(s): definition
            for s, definition in environment.get('variables', {}).items()
        }

        self._gen_symbols_cache()
        
        
        self._functions: dict[Symbol, FunctionDefinition] = {}
        
        if 'functions' in self._environment:
            for func_name, func_def in self._environment['functions'].items():
                
                func_args = [ self.deserialize_symbol(s) for s in func_def['args'] ]
                
                self._functions[self.deserialize_function(func_name)] = LmatEnvFunctionDefinition(
                    definition_store=self,
                    args=func_args,
                    latex_expr=func_def['expr'],
                    parser=parser
                )
    
    
    def get_function_definition(self, function: Function) -> FunctionDefinition | None:
        return self._functions.get(function)
    
    def deserialize_function(self, serialized_function: str) -> Function:
        return Function(serialized_function.strip())
    
    # Attempt to get the value which the given variable / symbol name should be substituted with.
    # If no such variable / symbol exists, returns None.
    def get_symbol_definition(self, symbol: Symbol) -> Expr | None:
        if symbol in self._cached_symbol_definitions:
            return self._cached_symbol_definitions[symbol]
        elif symbol in self._serialized_symbol_definitions:
            return self._deserialize_definition(symbol)  
        else:
            return None
        
    def deserialize_symbol(self, symbol_latex: str):
        return copy(self._cached_symbols.get(symbol_latex, Symbol(symbol_latex)))

    def _deserialize_definition(self, symbol: Symbol):
        serialized_definition = self._serialized_symbol_definitions[symbol]
        definition_value = self._parser.parse(serialized_definition, self)
        self._cached_symbols[symbol] = definition_value
        
        return definition_value

    def _gen_symbols_cache(self):
        tmp_cached_symbol_definitions = self._cached_symbol_definitions
        tmp_serialized_symbol_definitions = self._serialized_symbol_definitions
        
        # no symbol substitution should take place during cache generation,
        # so we temporarily clear these here.
        self._cached_symbol_definitions = {}
        self._serialized_symbol_definitions = {}
        
        for latex_str, assumptions_list in self._environment.get('symbols', {}).items():
            symbol = self._parser.parse(latex_str, self)
            
            if not isinstance(symbol, Symbol):
                raise RuntimeError(f'Symbol expression cannot be parsed as a symbol: "{latex_str}"')
            
            assumptions = { assumption: True for assumption in assumptions_list }
            
            self._cached_symbols[str(symbol)] = Symbol(str(symbol), **assumptions)
            
        self._cached_symbol_definitions = tmp_cached_symbol_definitions
        self._serialized_symbol_definitions = tmp_serialized_symbol_definitions


# wrapper class for a DefinitionStore, which maps function args and their corresponding symbols to a given set of values.
# should be used in the context of parsing a function body.
class LmantEnvFuncDefStore(DefinitionStore):
    
    def __init__(self, args: dict[Symbol, Expr], definitions_store: DefinitionStore):
        super().__init__()
        self._definitions_store = definitions_store
        self._args = args
    
    def get_function_definition(self, function):
        return self._definitions_store.get_function_definition(function)
    
    def deserialize_function(self, serialized_function):
        return self._definitions_store.deserialize_function(serialized_function)
    
    def get_symbol_definition(self, symbol: Symbol) -> Expr | None:
        return self._args.get(symbol, self._definitions_store.get_symbol_definition(symbol))

    def deserialize_symbol(self, serialized_symbol):
        return self._definitions_store.deserialize_symbol(serialized_symbol)
    
