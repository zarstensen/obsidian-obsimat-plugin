from modes.EvalModeBase import EvaluateMessage, eval_mode_base, try_assign

from ModeResponse import ModeResponse
from grammar.SympyParser import SympyParser

from sympy import *

## Tries to evaluate the last equality of an latex equation.
async def evalf_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):

        # If it is a dictonary, we cant call doit or simplify on it
        if not isinstance(sympy_expr, dict):
            sympy_expr = try_assign(sympy_expr.evalf(), sympy_expr)
        # TODO: Recursive call when it is returned
        
        return sympy_expr
           
    return await eval_mode_base(message, response, parser, evaluate)
