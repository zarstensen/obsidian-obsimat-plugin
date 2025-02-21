from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse
from grammar.SympyParser import SympyParser

from sympy import *
from typing import Any, TypedDict

class ConvertSympyModeMessage(TypedDict):
    expression: str
    environment: ObsimatEnvironment

# Parses a latex string into a sympy object.
async def convertSympyMode(message: ConvertSympyModeMessage, response: ModeResponse, parser: SympyParser):
    sympy_expr = parser.doparse(message['expression'], message['environment'])
    
    await response.result(sympy_expr)

# Returns a sympifyable version of the parsed sympy expression.
def convertSympyModeFormatter(sympy_expr: Any, _status: str, _metadata: dict) -> str:
    return str(sympy_expr)
