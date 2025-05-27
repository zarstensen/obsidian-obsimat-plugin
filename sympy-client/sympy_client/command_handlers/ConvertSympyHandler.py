from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.grammar.SympyParser import SympyParser
from .CommandHandler import CommandHandler, CommandResult

from sympy import *
from typing import Any, TypedDict, override

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
    def __init__(self, parser: SympyParser):
        super().__init__()
        self._parser = parser
        
    @override
    def handle(self, message: ConvertSympyModeMessage):
        return ConvertSympyResult(
            self._parser.doparse(message['expression'], message['environment'])
        )
