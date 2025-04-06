from modes.EvalModeBase import EvaluateMessage, eval_mode_base, try_assign
from ModeResponse import ModeResponse
from grammar.SympyParser import SympyParser

from sympy import *

## Tries to evaluate the last equality of an latex equation.
async def eval_handler(message: EvaluateMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):

        if isinstance(sympy_expr, dict):
            res = {}
            for key, value in sympy_expr.items():
                new_key = evaluate(key)
                new_value = evaluate(value)
                res[new_key] = new_value
            sympy_expr = res
        else:
            sympy_expr = try_assign(sympy_expr.doit(), sympy_expr)
            sympy_expr = try_assign(sympy_expr.simplify(), sympy_expr)
        return sympy_expr
           
    return await eval_mode_base(message, response, parser, evaluate)
