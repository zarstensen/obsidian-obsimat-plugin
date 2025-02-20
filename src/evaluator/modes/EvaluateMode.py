from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from grammar.SympyParser import SympyParser
from grammar.SystemOfExpr import SystemOfExpr

from copy import deepcopy
from sympy import *
from sympy.core.relational import Relational
from sympy.core.operations import LatticeOp, AssocOp
from typing import TypedDict

def __try_assign(new_value, original_value):
    if new_value is not None:
        return new_value
    else:
        return original_value

class EvaluateModeMessage(TypedDict):
    expression: str
    environment: ObsimatEnvironment

## Tries to evaluate the last equality of an latex equation.
async def evaluateMode(message: EvaluateModeMessage, response: ModeResponse, parser: SympyParser):    
    with evaluate(False):
        sympy_expr = parser.doparse(message['expression'], message['environment'])
    
    expr_lines = None
    
    # choose bottom / right hand most evaluatable expression.
    while isinstance(sympy_expr, SystemOfExpr) or isinstance(sympy_expr, Relational) or isinstance(sympy_expr, LatticeOp):
        # for system of expressions, take the last one
        if isinstance(sympy_expr, SystemOfExpr):
            expr_lines = (sympy_expr.get_location(-1).line, sympy_expr.get_location(-1).end_line)
            sympy_expr = sympy_expr.get_expr(-1)
        # for equalities, take the right hand side.
        if isinstance(sympy_expr, Relational):
            sympy_expr = sympy_expr.rhs
        # for boolean operations, eg. (a + b V a + c V b + c), then we choose the right most one (b + c).
        elif isinstance(sympy_expr, LatticeOp):
            sympy_expr = AssocOp.make_args(sympy_expr)[-1]

    # store expression before units are converted and it is evaluated,
    # so we can display this intermediate step in the result.
    before_evaluate = deepcopy(sympy_expr)
    sympy_expr = ObsimatEnvironmentUtils.substitute_units(sympy_expr, message['environment'])

    sympy_expr = __try_assign(sympy_expr.doit(), sympy_expr)
    sympy_expr = __try_assign(sympy_expr.expand(),  sympy_expr)
    sympy_expr = __try_assign(sympy_expr.simplify(), sympy_expr)
    
    if sympy_expr != before_evaluate:
        sympy_expr = Eq(before_evaluate, sympy_expr, evaluate=False)
    
    if expr_lines:
        await response.result(sympy_expr, metadata={ "start_line": expr_lines[0], "end_line": expr_lines[1] })
    else:
        await response.result(sympy_expr)
