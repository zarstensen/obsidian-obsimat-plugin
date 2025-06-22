from typing import Any, Literal, TypedDict, override

from sympy import *
from sympy.logic.boolalg import Boolean
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.grammar.SystemOfExpr import SystemOfExpr
from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.LmatLatexPrinter import lmat_latex

from .CommandHandler import *


class TruthTableMessage(TypedDict):
    expression: str
    environment: LmatEnvironment

class TruthTableResult(CommandResult):
    
    def __init__(self, columns: tuple[Expr], truth_table: tuple[tuple[Boolean]]):
        super().__init__()
        self.columns = columns
        self.truth_table = truth_table
    
# Inherit from EvalHandlerBase, override its thing so the result is taken from its result,
# evaluate should do nothing, not even simplify.
# then use dependency injection for the result objects.
class TruthTableHandler(EvalHandlerBase):
    
    def __init__(self, parser: SympyParser):
        super().__init__()
        self._parser = parser

    @override
    def handle(self, message: TruthTableMessage) -> SolveResult | MultivariateResult | ErrorResult:
