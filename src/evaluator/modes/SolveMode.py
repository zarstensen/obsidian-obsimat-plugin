from ObsimatClient import ObsimatClient
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils

from ObsimatEnvironment import ObsimatEnvironment
from sympy import *
from typing import Any, TypedDict


class SolveModeMessage(TypedDict):
    expression: str
    symbol: str | None
    environment: ObsimatEnvironment

# tries to solve the given latex expression.
# if a symbol is not given, and the expression is multivariate, this mode sends a response with status multivariate_equation,
# along with a list of possible symbols to solve for in its symbols key.
# if successfull its sends a message with status solved, and the result in the result key.
async def solveMode(message: SolveModeMessage, obsimat: ObsimatClient):
    expression = ObsimatEnvironmentUtils.parse_latex(message['expression'], message['environment'])
    expression = ObsimatEnvironmentUtils.substitute_units(expression, message['environment'])

    if 'symbol' not in message and len(expression.free_symbols) > 1:
        await obsimat.sendResult({"status": "multivariate_equation", "symbols": [str(s) for s in expression.free_symbols]})
        return

    if 'symbol' in message:
        for free_symbol in expression.free_symbols:
            if str(free_symbol) == message['symbol']:
                symbol = free_symbol
                break

        if symbol is None:
            await obsimat.sendError(f"No such symbol: {message['symbol']}")
            return
    else:
        symbol = list(expression.free_symbols)[0]

    solution_set = solveset(expression, symbol)

    # if solution is finite set, do magic, otherwise do simple stuff

    if type(solution_set) is FiniteSet:
        solutions = []
        for solution in list(solution_set):
            solutions.append(f"{symbol} = {latex(solution)}")
        await obsimat.sendResult({"status": "solved", "result": ' \\vee '.join(solutions)})
    else:
        await obsimat.sendResult({"status": "solved", "result": f"{symbol} \\in {latex(solution_set)}"})
