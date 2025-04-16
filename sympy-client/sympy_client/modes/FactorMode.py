from .EvalModeBase import EvaluateMessage, eval_mode_base
from sympy_client.ModeResponse import ModeResponse
from sympy_client.grammar.SympyParser import SympyParser

from sympy import *

async def factor_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):
        sympy_expr = sympy_expr.doit()
        sympy_expr = simplify(sympy_expr)
        sympy_expr = factor(sympy_expr)
        
        return sympy_expr
           
    return await eval_mode_base(message, response, parser, evaluate)
