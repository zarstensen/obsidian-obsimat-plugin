from ObsimatEnvironment import ObsimatEnvironment
from ClientBase import ClientBase
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from copy import deepcopy

from sympy import *
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
async def evaluateMode(message: EvaluateModeMessage, obsimat: ClientBase):
    expression = message['expression'].split("=")[-1]

    sympy_expr = ObsimatEnvironmentUtils.parse_latex(expression, message['environment'])

    # store expression before units are converted and it is evaluated,
    # so we can display this intermediate step in the result.
    before_units = deepcopy(sympy_expr)
    sympy_expr = ObsimatEnvironmentUtils.substitute_units(sympy_expr, message['environment'])

    sympy_expr = __try_assign(sympy_expr.doit(), sympy_expr)
    sympy_expr = __try_assign(sympy_expr.expand(),  sympy_expr)
    sympy_expr = __try_assign(sympy_expr.simplify(), sympy_expr)
    
    with evaluate(False):
        result = latex(Eq(before_units, sympy_expr), mat_symbol_style="bold")
    
    # TODO: this should be done with the regex package instead,
    # to ensure consistency among package usage.
    result = re.sub(r"\\text\{(.*?)\}", r"\1", result)

    await obsimat.sendSympyResult(result)