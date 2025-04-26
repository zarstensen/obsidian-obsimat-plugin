from dataclasses import dataclass
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from .SympyParser import SympyParser
from sympy import *
from copy import deepcopy
from typing import Callable, Iterable, Iterator
from sympy.core.symbol import Symbol

# The FunctionStore class is responsible for managing and parsing all defined functions in a given obsimat environment.
class FunctionStore:
    def __init__(self, environment: ObsimatEnvironment, parser: SympyParser):
        self._functions: dict[Symbol, FunctionStore._FunctionEntry] = {}
        
        if 'functions' in environment:
            for func_symbol, func_def in environment['functions'].items():
                self._functions[Symbol(func_symbol)] = FunctionStore._FunctionEntry(
                    args=symbols(func_def['args']),
                    latex_expr=func_def['expr'],
                    env=environment,
                    parser=parser
                )
    
    # check if the given symbol has a function tied to it.
    def has_function(self, symbol: Symbol) -> bool:
        return symbol in self._functions
    
    def get_function(self, func_symbol: Symbol) -> 'FunctionStore._FunctionEntry':
        assert self.has_function(func_symbol), f"Function {func_symbol} not found in function store."
        return self._functions[func_symbol]

    def __getitem__(self, func_symbol: Symbol) -> 'FunctionStore._FunctionEntry':
        return self.get_function(func_symbol)

    def __contains__(self, symbol) -> bool:
        if isinstance(symbol, Symbol):
            return self.has_function(symbol)
        else:
            return False

    class _FunctionEntry:
        
        def __init__(self, args: Iterable[Symbol], latex_expr: str, env: ObsimatEnvironment, parser: SympyParser):
            self._args = tuple(args)
            self._latex_expr = latex_expr
            self._env = env
            self._parser = parser

        @property
        def args(self) -> tuple[Symbol]:
            return self._args

        @property
        def latex_expr(self) -> str:
            return self._latex_expr

        def call(self, *args) -> Expr:
            assert len(args) == len(self._args)

            eval_env: dict = deepcopy(self._env)
            
            if 'variables' not in eval_env:
                eval_env['variables'] = {}
            
            for arg_symbol, arg_value in zip(self.args, args):
                eval_env['variables'][str(arg_symbol)] = arg_value
            
            expr = self._parser.doparse(self.latex_expr, eval_env)
            
            return expr
        
        def parse_body(self):
            return self.call(*self.args)



    
