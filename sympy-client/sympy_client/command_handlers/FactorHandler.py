from typing import Any, override
from .EvalHandlerBase import EvalHandlerBase, EvaluateMessage
from sympy_client.grammar.SympyParser import SympyParser

from sympy import *

class FactorHandler(EvalHandlerBase):
    def __init__(self, parser: SympyParser):
        super().__init__(parser)

    @override
    def evaluate(self, sympy_expr: Expr, _message: EvaluateMessage) -> Expr:
        return factor(simplify(sympy_expr.doit()))