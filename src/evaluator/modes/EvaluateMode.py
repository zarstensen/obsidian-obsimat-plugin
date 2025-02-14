from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from grammar import ObsimatLatexParser
from copy import deepcopy

from sympy import *
from sympy.core.relational import Relational
from typing import Any, TypedDict
import re

def __try_assign(new_value, original_value):
    if new_value is not None:
        return new_value
    else:
        return original_value

class EvaluateModeMessage(TypedDict):
    expression: str
    environment: ObsimatEnvironment

## Tries to evaluate the last equality of an latex equation.
async def evaluateMode(message: EvaluateModeMessage, response: ModeResponse, parser: ObsimatLatexParser):
    # TODO: replace this with retreiving the right most side of any sympy equality returned from the parser.
    # if a system of expressions, use the bottom one.
    # expression = message['expression'].split("=")[-1]

    parser.set_environment(message['environment'])
    
    with evaluate(False):
        sympy_expr = parser.doparse(message['expression'])

    # choose last expression in system of equations.
    if isinstance(sympy_expr, list):
        sympy_expr = sympy_expr[-1]
    
    # choose right hand most evaluatable expression.
    while isinstance(sympy_expr, Relational):
        sympy_expr = sympy_expr.rhs

    # store expression before units are converted and it is evaluated,
    # so we can display this intermediate step in the result.
    before_units = deepcopy(sympy_expr)
    sympy_expr = ObsimatEnvironmentUtils.substitute_units(sympy_expr, message['environment'])

    sympy_expr = __try_assign(sympy_expr.doit(), sympy_expr)
    sympy_expr = __try_assign(sympy_expr.expand(),  sympy_expr)
    sympy_expr = __try_assign(sympy_expr.simplify(), sympy_expr)
    
    with evaluate(False):
        await response.result(Eq(before_units, sympy_expr))
