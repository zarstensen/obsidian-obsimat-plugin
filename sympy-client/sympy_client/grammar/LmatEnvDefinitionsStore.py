from typing import Iterable
from .SympyParser import DefinitionsStore

from sympy import Symbol, Expr, Function, symbols
from copy import copy, deepcopy
from .SympyParser import SympyParser, FunctionDefinition
from ..LmatEnvironment import LmatEnvironment

class LmatEnvFunctionDefinition(FunctionDefinition):
    def __init__(self, definition_store: DefinitionsStore, parser: SympyParser, args: Iterable[Symbol], latex_expr: str):
        super().__init__()
        self._definitions_store = definition_store
        self._parser = parser
        self.args = tuple(args)
        self.latex_expr = latex_expr

    def call(self, *args) -> Expr:
        assert len(args) == len(self.args)

        args_map = { arg: val for arg, val in zip(self.args, args) }
        func_def_store = LmantEnvFuncDefStore(args_map, self._definitions_store)
        
        expr = self._parser.parse(self.latex_expr, func_def_store)
        
        return expr
    
    def get_body(self):
        return self.call(*self.args)

# implement this
class LmatEnvDefStore(DefinitionsStore):
    
    def __init__(self, parser: SympyParser, environment: LmatEnvironment):
        super().__init__()
        
        self._parser = parser
        
        self._environment = environment
        
        # this is a bit cursed.
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
        tmp_symbol_cache = self._cached_symbol_definitions
        tmp_symbol_definitions = self._serialized_symbol_definitions
        
        self._cached_symbol_definitions = {}
        self._serialized_symbol_definitions = {}
        
        for latex_str, assumptions_list in self._environment.get('symbols', {}).items():
            symbol = self._parser.parse(latex_str, self)
            
            if not isinstance(symbol, Symbol):
                raise RuntimeError(f'Symbol expression cannot be parsed as a symbol: "{latex_str}"')
            
            assumptions = { assumption: True for assumption in assumptions_list }
            
            self._cached_symbols[str(symbol)] = Symbol(str(symbol), **assumptions)
            
        self._cached_symbol_definitions = tmp_symbol_cache
        self._serialized_symbol_definitions = tmp_symbol_definitions



class LmantEnvFuncDefStore(DefinitionsStore):
    
    def __init__(self, args: dict[Symbol, Expr], definitions_store: DefinitionsStore):
        super().__init__()
        self._definitions_store = definitions_store
        self._args = args
    
    def get_function_definition(self, function):
        return super().get_function_definition(function)
    
    def deserialize_function(self, serialized_function):
        return super().deserialize_function(serialized_function)
    
    def get_symbol_definition(self, symbol: Symbol) -> Expr | None:
        return self._args.get(symbol, super().get_symbol_definition(symbol))

    def deserialize_symbol(self, serialized_symbol):
        return super().deserialize_symbol(serialized_symbol)
    
