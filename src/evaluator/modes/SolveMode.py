from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse
from grammar.SystemOfExpr import SystemOfExpr
from grammar.SympyParser import SympyParser

from sympy import *
from typing import Any, TypedDict

from sympy.solvers.solveset import NonlinearError

class SolveModeMessage(TypedDict):
    expression: str
    symbol: str | None
    environment: ObsimatEnvironment
    
# The maximum number of finite solution to display it as a disjunction of solutions.
# instead of the set itself.
MAX_RELATIONAL_FINITE_SOLUTIONS = 5

# tries to solve the given latex expression.
# if a symbol is not given, and the expression is multivariate, this mode sends a response with status multivariate_equation,
# along with a list of possible symbols to solve for in its symbols key.
# if successfull its sends a message with status solved, and the result in the result key.
async def solveMode(message: SolveModeMessage, response: ModeResponse, parser: SympyParser):    
    equations = parser.doparse(message['expression'], message['environment'])
    equations = ObsimatEnvironmentUtils.substitute_units(equations, message['environment'])

    # position information is not needed here,
    # so extract the equations into a tuple, which sympy can work with.
    if isinstance(equations, SystemOfExpr):
        equations = equations.get_all_expr()
    else:
        equations = (equations,)

    # get a list of free symbols, by combining all the equations individual free symbols.
    free_symbols = set()
    
    for equation in equations:
        free_symbols.update(equation.free_symbols)

    if len(free_symbols) == 0:
        await response.error("Cannot solve equation if no free symbols are present.")
        return

    free_symbols = sorted(list(free_symbols), key=str)

    domain = S.Complexes
    
    if 'domain' in message['environment'] and message['environment']['domain'].strip() != "":
        domain = sympify(message['environment']['domain'])

    # determine what symbols to solve for
    if 'symbols' not in message and len(free_symbols) > len(equations):
        await response.result({ 'symbols': free_symbols, 'equation_count': len(equations) }, status="multivariate_equation")
        return

    if 'symbols' in message and len(message['symbols']) != len(equations):
        await response.error("Incorrect number of symbols provided.")
        return

    symbols = []

    if 'symbols' in message:
        for free_symbol in free_symbols:
            if str(free_symbol) in message['symbols']:
                symbols.append(free_symbol)

        if len(symbols) != len(equations):
            await response.error(f"No such symbols: {message['symbols']}")
            return
    else:
        symbols = list(free_symbols)
    
    
    # TODO: is there another way to do this?
    # it is sortof a mess having to distinguish between strictly 1 equation and multiple equations.
    
    print(symbols, flush=True)
    
    if len(equations) == 1 and len(symbols) == 1: # these two should always have equal lenth.
        solution_set = solveset(equations[0], symbols[0], domain=domain)
    else:
        try:
            solution_set = linsolve(equations, symbols)
        except NonlinearError:
            solution_set = nonlinsolve(equations, symbols)
    
    await response.result({ 'solution': solution_set, 'symbols': symbols })

# Convert a result returned from solveMode, into a json encodable string.
def solveModeFormatter(result: Any, status: str, _metadata: dict) -> str:
    # return list of all possible symbols to solve for.
    # include the sympy comparable string version, and a latex version, which should only be used for visuals.
    if status == 'multivariate_equation':
        result['symbols'] = [ { "sympy_symbol": str(s), "latex_symbol": latex(s) } for s in result['symbols'] ]
        return result
    
    # format the solution set, depending on its type and size.
    elif status=='success':
        
        solutions_set = result['solution']
        
        if len(result['symbols']) == 1:
            symbols = result['symbols'][0]
        else:
            symbols = tuple(result['symbols'])
        
        if isinstance(solutions_set, FiniteSet) and len(solutions_set) <= MAX_RELATIONAL_FINITE_SOLUTIONS:
            return latex(solutions_set.as_relational(symbols))
        else:
            return f"{latex(symbols)} \\in {latex(solutions_set)}"
