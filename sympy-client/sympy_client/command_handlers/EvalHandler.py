from typing import override
from .EvalHandlerBase import EvalHandlerBase, EvaluateMessage
from sympy_client.grammar.SympyParser import DefStoreLarkCompiler

from sympy import *

class EvalHandler(EvalHandlerBase):
    def __init__(self, parser: DefStoreLarkCompiler):
        super().__init__(parser)

    @override
    def evaluate(self, sympy_expr: Expr, _message: EvaluateMessage) -> Expr:  
        return simplify(sympy_expr.doit())
