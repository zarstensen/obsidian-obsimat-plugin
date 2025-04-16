from .EvalModeBase import EvaluateMessage, eval_mode_base
from sympy_client.ModeResponse import ModeResponse
from sympy_client.grammar.SympyParser import SympyParser

from sympy import *

async def apart_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):
        sympy_expr = sympy_expr.doit()
        sympy_expr = simplify(sympy_expr.simplify())
        sympy_expr = apart(sympy_expr.apart())
        
        return sympy_expr
           
    return await eval_mode_base(message, response, parser, evaluate)
