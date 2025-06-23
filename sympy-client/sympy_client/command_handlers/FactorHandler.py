from typing import override

from sympy import *

from sympy_client.grammar.SympyParser import SympyParser

from .EvalHandlerBase import EvalHandlerBase, EvaluateMessage


class FactorHandler(EvalHandlerBase):
    def __init__(self, parser: SympyParser):
        super().__init__(parser)

    @override
    def evaluate(self, sympy_expr: Expr, _message: EvaluateMessage) -> Expr:
        return factor(simplify(sympy_expr.doit()))
