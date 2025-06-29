from abc import ABC, abstractmethod
from typing import TypedDict, override

from sympy import *
from sympy.core.relational import Relational
from sympy.physics.units.unitsystem import UnitSystem

import sympy_client.UnitsUtils as UnitsUtils
from sympy_client.grammar.LmatEnvDefStore import LmatEnvDefStore
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.grammar.SystemOfExpr import SystemOfExpr
from sympy_client.grammar.transformers.PropositionsTransformer import PropositionExpr
from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.LmatLatexPrinter import lmat_latex

from .CommandHandler import CommandHandler, CommandResult


class EvalResult(CommandResult, ABC):
    def __init__(self, sympy_expr: Expr, expr_separator: str, expr_lines: list[int] | None):
        super().__init__()
        self.sympy_expr = sympy_expr
        self.expr_separator = expr_separator
        self.expr_lines = expr_lines

    @override
    def getPayload(self):
        metadata = dict(separator = self.expr_separator)

        if self.expr_lines is not None and self.expr_lines[0] != self.expr_lines[1]:
            metadata = dict(
                **metadata,
                start_line = self.expr_lines[0],
                end_line = self.expr_lines[1]
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
        definitions_store = LmatEnvDefStore(self._parser, message['environment'])
        sympy_expr = self._parser.parse(message['expression'], definitions_store)
        expr_lines = None

        # choose bottom / right most evaluatable expression.
        while isinstance(sympy_expr, SystemOfExpr) or isinstance(sympy_expr, Relational):
            # for system of expressions, take the last one
            if isinstance(sympy_expr, SystemOfExpr):
                expr_lines = (sympy_expr.get_location(-1).line, sympy_expr.get_location(-1).end_line)

                if expr_lines[1] is None:
                    expr_lines = (expr_lines[0], len(message['expression'].splitlines()))

                sympy_expr = sympy_expr.get_expr(-1)

            # for equalities, take the right hand side.
            if isinstance(sympy_expr, Relational):
                sympy_expr = sympy_expr.rhs

        if isinstance(sympy_expr, PropositionExpr):
            sympy_expr = sympy_expr.expr
            separator = r"\equiv"
        else:
            separator = "="

        sympy_expr = self.evaluate(sympy_expr, message)

        unit_system = message['environment'].get('unit_system', None)

        if unit_system is not None:
            sympy_expr = UnitsUtils.auto_convert(sympy_expr, UnitSystem.get_unit_system(unit_system))
        else:
            sympy_expr = UnitsUtils.auto_convert(sympy_expr)


        return EvalResult(sympy_expr, separator, expr_lines)
