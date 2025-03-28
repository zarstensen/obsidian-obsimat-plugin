from modes.EvalModeBase import EvaluateMessage, eval_mode_base, try_assign
from ModeResponse import ModeResponse
from grammar.SympyParser import SympyParser

from sympy import *

async def apart_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):
        sympy_expr = try_assign(sympy_expr.doit(), sympy_expr)
        sympy_expr = try_assign(sympy_expr.simplify(), sympy_expr)
        sympy_expr = try_assign(sympy_expr.apart(), sympy_expr)
        
        return sympy_expr
           
    return await eval_mode_base(message, response, parser, evaluate)
