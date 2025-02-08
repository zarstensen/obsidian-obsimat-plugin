from sympy.parsing.latex import parse_latex_lark
from lark import Tree
import sympy.physics.units as u

class LatexParser:
    @staticmethod
    def parse_latex(latex_str: str):
        sympy_expr = parse_latex_lark(latex_str)

        if type(sympy_expr) is Tree:
            sympy_expr = sympy_expr.children[0]

            # units on / off here for the future
        if False:
            for symbol in sympy_expr.free_symbols:
                try:
                    units = u.find_unit(str(symbol))
                    if units[0] == str(symbol):
                        sympy_expr = sympy_expr.subs({symbol: getattr(u, units[0])})
                except AttributeError:
                    continue

        return sympy_expr
