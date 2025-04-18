from .CommandHandler import CommandResult, CommandHandler
from typing import Any, TypedDict
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.grammar.SystemOfExpr import SystemOfExpr
from sympy_client.ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.SympyUtils import sympy_expr_to_latex
from sympy_client.ObsimatEnvironment import ObsimatEnvironment

from copy import deepcopy
from sympy import *
from sympy.core.relational import Relational
from sympy.core.operations import LatticeOp, AssocOp
from typing import Any, override

from abc import ABC, abstractmethod

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
                end_line = self.expr_lines[1]
            )
        
        return CommandResult.result(sympy_expr_to_latex(self.sympy_expr), metadata=metadata)

class EvaluateMessage(TypedDict):
    expression: str
    environment: ObsimatEnvironment

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
        before_evaluate = deepcopy(sympy_expr)
        sympy_expr = ObsimatEnvironmentUtils.substitute_units(sympy_expr, message['environment'])

        sympy_expr = self.evaluate(sympy_expr, message)

        if sympy_expr != before_evaluate:
            sympy_expr = Eq(before_evaluate, sympy_expr, evaluate=False)
            
        return EvalResult(sympy_expr, expr_lines)
