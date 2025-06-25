import re as regex
from functools import reduce

from sympy import *
from sympy.physics.units import Quantity
from sympy.printing.latex import LatexPrinter

from sympy_client.grammar.LatexMatrix import LatexMatrix


# this is a bit scuffed, but since the Quantity class, and not the printer class, implements a _latex method,
# the printer class prioritizes this over a potential _print_Quantity in the LmatLatexPrinter.
# this could probably be solved by renaming the _printmethod in LmatLatexPrinter to _lmat_latex f.ex.
def _quantity_latex(self, _printer):
    if self._latex_repr:
        return f"{{{self._latex_repr}}}"
    else:
        return f"{{{self.args[1] if len(self.args) >= 2 else self.args[0]}}}"


Quantity._latex = _quantity_latex


# Convert a sympy expression to a formatted latex string.
class LmatLatexPrinter(LatexPrinter):
    def __init__(self, settings={}):
        # use \, instead of whitespace, to add spacing in rendered latex.
        if "mul_symbol" not in settings:
            settings["mul_symbol"] = r" \, "
        super().__init__(settings)

    def doprint(self, expr):
        # remove all \text latex, we do not want this.
        return regex.sub(r"\\text\{(.*?)\}", r"\1", super().doprint(expr))

    def _print_LatexMatrix(self, expr: LatexMatrix):
        contents = []

        for row_index in range(expr.rows):
            contents_row = []
            for elem in expr[row_index, :]:
                contents_row.append(self._print(elem))
            contents.append(" & ".join(contents_row))

        return f"{expr.env_begin}{r' \\ '.join(contents)}{expr.env_end}"

    def _print_Mul(self, expr: Mul):
        # try to split any fraction up into at most 3 distinct fractions.
        # one for all constant values, one for all symbols, and finally one for all units.

        numerator, denominator = fraction(expr)

        if denominator == S.One:
            return super()._print_Mul(expr)

        num_const, num_sym, num_unit = self._filter_expr(numerator)
        den_const, den_sym, den_unit = self._filter_expr(denominator)

        const_value = None

        if num_const == S.One or num_const == S.NegativeOne:
            den_sym *= den_const
            num_sym *= num_const
        else:
            const_value = num_const / den_const

        sym_value = None
        if num_sym != 1 or den_sym != 1:
            sym_value = num_sym / den_sym

        unit_value = None
        if num_unit != 1 or den_unit != 1:
            unit_value = num_unit / den_unit

        result = self._settings["mul_symbol_latex"].join(
            [
                super()._print_Mul(e)
                for e in filter(
                    lambda x: x is not None, [const_value, sym_value, unit_value]
                )
            ]
        )

        return result

    # split expr into 3 expr.
    # the first contains all constants in the passed expression,
    # the second contains all symbols in the passed expression,
    # the third contains all units in the passed expressions.
    def _filter_expr(self, expr: Expr):
        args = []

        if expr.is_Mul:
            args = expr.args
        elif isinstance(expr, Quantity) or isinstance(expr, Pow) or expr.is_number:
            args = [expr]
        else:
            return (1, expr, 1)

        constants, non_constants = sift(args, lambda a: a.is_number, binary=True)
        units, symbols = sift(
            non_constants,
            lambda s: isinstance(s, Quantity)
            or isinstance(s, Pow)
            and isinstance(s.base, Quantity),
            binary=True,
        )

        return (
            reduce(lambda x, y: x * y, constants, 1),
            reduce(lambda x, y: x * y, symbols, 1),
            reduce(lambda x, y: x * y, units, 1),
        )


def lmat_latex(expr: Expr) -> str:
    return LmatLatexPrinter().doprint(expr)
