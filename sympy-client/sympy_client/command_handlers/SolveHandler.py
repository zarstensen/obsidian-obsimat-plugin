from sympy_client.ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from sympy_client.ObsimatClient import ObsimatClient
from sympy_client.grammar.SystemOfExpr import SystemOfExpr
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.SympyUtils import sympy_expr_to_latex
from .CommandHandler import *

from dataclasses import dataclass
from sympy import *
from sympy.solvers.solveset import NonlinearError
from typing import Any, TypedDict, override


class SolveModeMessage(TypedDict):
    expression: str
    symbol: str | None
    environment: ObsimatEnvironment

class MultivariateResult(CommandResult):
    
    def __init__(self, symbols, equation_count: int):
        super().__init__()
        self.symbols = symbols
        self.equation_count = equation_count
        
    @override
    def getPayload(self) -> dict:
        
        result = dict(
            equation_count=self.equation_count,
            symbols=[ dict(sympy_symbol=str(s), latex_symbol=sympy_expr_to_latex(s)) for s in self.symbols ]
        )
        
        return CommandResult.result(result, status='multivariate_equation')
    
class SolveResult(CommandResult):
    
    # The maximum number of finite solution to display it as a disjunction of solutions.
    # instead of the set itself.
    MAX_RELATIONAL_FINITE_SOLUTIONS = 5
    
    
    def __init__(self, solution: Any, symbols: list[Any]):
        super().__init__()
        self.solution = solution
        self.symbols = symbols
    
    @override
    def getPayload(self) -> dict:
        solutions_set = self.solution
        
        if len(self.symbols) == 1:
            symbols = self.symbols[0]
        else:
            symbols = tuple(self.symbols)
        
        if isinstance(solutions_set, FiniteSet) and len(solutions_set) <= SolveResult.MAX_RELATIONAL_FINITE_SOLUTIONS:
            return CommandResult.result(sympy_expr_to_latex(solutions_set.as_relational(symbols)))
        else:
            return CommandResult.result(
                f"{sympy_expr_to_latex(symbols)} \\in {sympy_expr_to_latex(solutions_set)}"
            )


# tries to solve the given latex expression.
# if a symbol is not given, and the expression is multivariate, this mode sends a response with status multivariate_equation,
# along with a list of possible symbols to solve for in its symbols key.
# if successfull its sends a message with status solved, and the result in the result key.
class SolveHandler(CommandHandler):
    
    def __init__(self, parser: SympyParser):
        super().__init__()
        self._parser = parser

    @override
    def handle(self, message: SolveModeMessage) -> SolveResult | MultivariateResult | ErrorResult:
        equations = self._parser.doparse(message['expression'], message['environment'])
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
            return ErrorResult("Cannot solve equation if no free symbols are present.")

        free_symbols = sorted(list(free_symbols), key=str)

        domain = S.Complexes
        
        if 'domain' in message['environment'] and message['environment']['domain'].strip() != "":
            domain = sympify(message['environment']['domain'])

        # determine what symbols to solve for
        if 'symbols' not in message and len(free_symbols) > len(equations):
            return MultivariateResult(free_symbols, len(equations))

        if 'symbols' in message and len(message['symbols']) != len(equations):
            return ErrorResult("Incorrect number of symbols provided.")

        symbols = []

        if 'symbols' in message:
            for free_symbol in free_symbols:
                if str(free_symbol) in message['symbols']:
                    symbols.append(free_symbol)

            if len(symbols) != len(equations):
                return ErrorResult(f"No such symbols: {message['symbols']}")
        else:
            symbols = list(free_symbols)
        
        
        # TODO: is there another way to do this?
        # it is sortof a mess having to distinguish between strictly 1 equation and multiple equations.
        
        if len(equations) == 1 and len(symbols) == 1: # these two should always have equal lenth.
            solution_set = solveset(equations[0], symbols[0], domain=domain)
        else:
            try:
                solution_set = linsolve(equations, symbols)
            except NonlinearError:
                solution_set = nonlinsolve(equations, symbols)
        
        return SolveResult(solution_set, symbols)
