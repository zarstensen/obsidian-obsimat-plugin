from typing import TypedDict, override

from sympy import *
from sympy_client.grammar.LmatEnvDefStore import LmatEnvDefStore
from sympy_client.grammar.SympyParser import DefStoreLarkCompiler
from sympy_client.LmatEnvironment import LmatEnvironment

from .CommandHandler import CommandHandler, CommandResult


class ConvertSympyResult(CommandResult):
    
    def __init__(self, sympy_expr):
        super().__init__()
        self.sympy_expr = sympy_expr
       
    @override 
    def getPayload(self) -> dict:
        return CommandResult.result(str(self.sympy_expr))

class ConvertSympyModeMessage(TypedDict):
    expression: str
    environment: LmatEnvironment

class ConvertSympyHandler(CommandHandler):
    def __init__(self, expr_compiler: DefStoreLarkCompiler, symbols_compiler: DefStoreLarkCompiler):
        super().__init__()
        self._expr_compiler = expr_compiler
        self._symbols_compiler = symbols_compiler
        
    @override
    def handle(self, message: ConvertSympyModeMessage):
        environment: LmatEnvironment = message['environment']
        expression: str = message['expression']
        
        def_store = LmatEnvDefStore(message['environment'], expression)
        
        # TODO: add support for functions.
        
        # build a dependency graph for the variables present in the expression.
        
        expression_dependencies: set[Symbol] = set(self._symbols_compiler.compile(expression, LmatEnvDefStore({})))
        
        dependency_graph: dict[Symbol, set[Symbol]] = {}
        
        for dep in expression_dependencies:
            dependency_graph[dep] = def_store.get_symbol_dependencies(dep)
        
        
        
        return ConvertSympyResult(
            self._expr_compiler.compile(message['expression'], )
        )
