from .EvalModeBase import EvaluateMessage, eval_mode_base

from sympy_client.ModeResponse import ModeResponse
from sympy_client.grammar.SympyParser import SympyParser

from sympy import *

## Tries to evaluate the last equality of an latex equation.
async def evalf_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):
        return sympy_expr.evalf()
           
    return await eval_mode_base(message, response, parser, evaluate)
