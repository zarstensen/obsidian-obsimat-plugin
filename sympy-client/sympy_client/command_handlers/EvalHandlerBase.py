from abc import ABC, abstractmethod
from copy import deepcopy
from typing import TypedDict, override

from sympy import *
from sympy.core.operations import AssocOp, LatticeOp
from sympy.core.relational import Relational
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.grammar.SystemOfExpr import SystemOfExpr
from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.LmatEnvironmentUtils import LmatEnvironmentUtils
from sympy_client.LmatLatexPrinter import lmat_latex

from .CommandHandler import CommandHandler, CommandResult


class EvalResult(CommandResult, ABC):
    def __init__(self, sympy_expr: Expr, expr_lines: list[int] | None):
        super().__init__()
        self.sympy_expr = sympy_expr
        self.expr_lines = expr_lines
    
    @override
    def getPayload(self):
        metadata = None
        
        if self.expr_lines is not None:
            metadata = dict(
                start_line = self.expr_lines[0],
                end_line = self.expr_lines[1] if self.expr_lines[1] is not None else self.expr_lines[0]
            )
        
        return CommandResult.result(lmat_latex(self.sympy_expr), metadata=metadata)

class EvaluateMessage(TypedDict):
    expression: str
    environment: LmatEnvironment

class EvalHandlerBase(CommandHandler, ABC):
    
    def __init__(self, parser: SympyParser):
        super().__init__()
        self._parser = parser
    
    @abstractmethod
    def evaluate(self, sympy_expr: Expr, message: EvaluateMessage) -> Expr:
        pass

    @override
    def handle(self, message: EvaluateMessage) -> EvalResult:
        sympy_expr = self._parser.doparse(message['expression'], message['environment'])
        expr_lines = None
        
        # choose bottom / right most evaluatable expression.
        while isinstance(sympy_expr, SystemOfExpr) or isinstance(sympy_expr, Relational) or isinstance(sympy_expr, LatticeOp):
            # for system of expressions, take the last one
            if isinstance(sympy_expr, SystemOfExpr):
                expr_lines = (sympy_expr.get_location(-1).line, sympy_expr.get_location(-1).end_line)
                sympy_expr = sympy_expr.get_expr(-1)
            # for equalities, take the right hand side.
            if isinstance(sympy_expr, Relational):
                sympy_expr = sympy_expr.rhs
            # for boolean operations, eg. (a + b V a + c V b + c), then we choose the right most one (b + c).
            elif isinstance(sympy_expr, LatticeOp):
                sympy_expr = AssocOp.make_args(sympy_expr)[-1]

        # store expression before units are converted and it is evaluated,
        # so we can display this intermediate step in the result.

        sympy_expr = LmatEnvironmentUtils.substitute_units(sympy_expr, message['environment'])
        sympy_expr = self.evaluate(sympy_expr, message)
  
        return EvalResult(sympy_expr, expr_lines)
