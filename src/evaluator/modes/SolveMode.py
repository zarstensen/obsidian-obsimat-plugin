from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse

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
async def solveMode(message: SolveModeMessage, response: ModeResponse):
    expression = ObsimatEnvironmentUtils.parse_latex(message['expression'], message['environment'])
    expression = ObsimatEnvironmentUtils.substitute_units(expression, message['environment'])

    if 'symbol' not in message and len(expression.free_symbols) > 1:
        await response.result(expression.free_symbols, status="multivariate_equation")
        return

    if 'symbol' in message:
        for free_symbol in expression.free_symbols:
            if str(free_symbol) == message['symbol']:
                symbol = free_symbol
                break

        if symbol is None:
            await response.error(f"No such symbol: {message['symbol']}")
            return
    else:
        symbol = list(expression.free_symbols)[0]

    solution_set = solveset(expression, symbol)
    
    await response.result({ 'solution': solution_set, 'symbol': symbol })

# Convert a result returned from solveMode, into a json encodable string.
def solveModeFormatter(result: Any, status: str, _metadata: dict) -> str:
    # return list of all possible symbols to solve for.
    if status == 'multivariate_equation':
        return [ str(s) for s in result ]
    
    # format the solution set, depending on its type and size.
    elif status=='success':
        if type(result['solution']) is FiniteSet and len(result['solution']) <= 5:
            return latex(result['solution'].as_relational(result['symbol']))
        else:
            return f"{result['symbol']} \\in {latex(result['solution'])}"
        
    # if solution is finite set, do magic, otherwise do simple stuff

