from dataclasses import dataclass
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from .SympyParser import SympyParser
from sympy import *
from copy import deepcopy
from typing import Callable, Iterator
from sympy.core.symbol import Symbol

# The FunctionStore class is responsible for managing and parsing all defined functions in a given obsimat environment.
class FunctionStore:
    def __init__(self, environment: ObsimatEnvironment, parser: SympyParser):
        self._functions: dict[Symbol, FunctionStore._FunctionEntry] = {}
        
        if 'functions' in environment:
            for func_symbol, func_def in environment['functions'].items():
                self._functions[Symbol(func_symbol)] = FunctionStore._FunctionEntry(
                    args=symbols(func_def['args']),
                    latex_expr=func_def['expr']
                )
        
        self._env = environment
        self._parser = parser
    
    # check if the given symbol has a function tied to it.
    def has_function(self, symbol: Symbol) -> bool:
        return symbol in self._functions

    # retreive an ordered (as in the order is the original order of the args) list of the function symbol arguments.
    def get_function_args(self, func_symbol: Symbol) -> list[Symbol]:
        return self._functions[func_symbol].args
    
    # retreive a parsed sympy expression representing the body of the function.
    # NOTE: this only works if all free symbols (including arguments) are NOT treated as matrices.
    def get_parsed_function_expr(self, func_symbol: Symbol) -> Expr:
        return self.call_function(func_symbol, *self.get_function_args(func_symbol))
    
    # call the function body tied to the given symbol with the given args.
    # this, in contrary to get_parsed_function_expr does work if the args are treated as matrices.
    def call_function(self, func_symbol: Symbol, *args) -> Expr:
        assert len(args) == len(self.get_function_args(func_symbol))
        
        eval_env: dict = deepcopy(self._env)
        
        if 'variables' not in eval_env:
            eval_env['variables'] = {}
        
        for arg_symbol, arg_value in zip(self.get_function_args(func_symbol), args):
            eval_env['variables'][str(arg_symbol)] = arg_value
        
        expr = self._parser.doparse(self._functions[func_symbol].latex_expr, eval_env)
        
        return expr

    def __contains__(self, symbol) -> bool:
        if isinstance(symbol, Symbol):
            return self.has_function(symbol)
        else:
            return False

    @dataclass
    class _FunctionEntry:
        args: set[Symbol]
        latex_expr: str
