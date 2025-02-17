from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from ObsimatEnvironment import ObsimatEnvironment
from ModeResponse import ModeResponse

from grammar.SystemOfExpr import SystemOfExpr
from grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy import *
from typing import Any, TypedDict

from sympy.solvers.solveset import NonlinearError

class SolveModeMessage(TypedDict):
    expression: str
    symbol: str | None
    environment: ObsimatEnvironment

# tries to solve the given latex expression.
# if a symbol is not given, and the expression is multivariate, this mode sends a response with status multivariate_equation,
# along with a list of possible symbols to solve for in its symbols key.
# if successfull its sends a message with status solved, and the result in the result key.
async def solveMode(message: SolveModeMessage, response: ModeResponse, parser: ObsimatLatexParser):
    parser.set_environment(message['environment'])
    equations = parser.doparse(message['expression'])
    equations = ObsimatEnvironmentUtils.substitute_units(equations, message['environment'])

    if isinstance(equations, SystemOfExpr):
        equations = equations.get_all_expr()
    else:
        equations = (equations,)

    free_symbols = set()
    
    for equation in equations:
        free_symbols.update(equation.free_symbols)

    free_symbols = sorted(list(free_symbols), key=str)

    domain = S.Complexes
    
    if 'domain' in message['environment']:
        domain = sympify(message['environment']['domain'])

    if 'symbols' not in message and len(free_symbols) > len(equations):
        await response.result({ 'symbols': free_symbols, 'equation_count': len(equations) }, status="multivariate_equation")
        return

    if 'symbols' in message and len(message['symbols']) != len(equation):
        await response.error("Incorrect number of symbols provided.")
        return

    symbols = []

    if 'symbols' in message:
        for free_symbol in free_symbols:
            if str(free_symbol) == message['symbols']:
                symbols.append(free_symbol)

        if len(symbols) != len(equations):
            await response.error(f"No such symbols: {message['symbols']}")
            return
    else:
        symbols = list(free_symbols)
        
    solution_set = None
        
    if len(symbols) == 1:
        solution_set = solveset(equations, symbols[0], domain=domain)
    else:
        try:
            solution_set = linsolve(equations, symbols)
        except NonlinearError:
            solution_set = nonlinsolve(equations, symbols)
    
    await response.result({ 'solution': solution_set, 'symbols': symbols })

# Convert a result returned from solveMode, into a json encodable string.
def solveModeFormatter(result: Any, status: str, _metadata: dict) -> str:
    # return list of all possible symbols to solve for.
    if status == 'multivariate_equation':
        return [ str(s) for s in result ]
    
    # format the solution set, depending on its type and size.
    elif status=='success':
        
        solutions_set = result['solution']
        
        if len(result['symbols']) == 1:
            symbols = result['symbols'][0]
        else:
            symbols = type(result['symbols'])
        
        if len(result['solution']) == 1 and isinstance(result['solution'].args[0], FiniteSet) and len(result['solution'].args[0]) <= 5:
            return result['solution'].as_relational(symbols)
        else:
            return f"{symbols} \\in {latex(result['solution'])}"
            

        for symbol, solution in zip(symbols, list(solutions_set)):  
            # if solution is finite set, do magic, otherwise do simple stuff
            if type(result['solution']) is FiniteSet and len(result['solution']) <= 5:
                result_str += f"{align_token}{latex(solution.as_relational(symbol))}{newline_token}"
            else:
                result_str += f"{symbol} {align_token}\\in {latex(solution)}{newline_token}"
                return f"{result['symbol']} \\in {latex(result['solution'])}"
        
        if len(symbols) > 1:
            result_str += "\\end{align}"
            
        return result_str

