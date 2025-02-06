from sympy import *
from sympy import sympify
from sympy.parsing.latex import parse_latex, parse_latex_lark
from sympy.solvers.solveset import NonlinearError
from lark import Tree
import sympy.physics.units as u

m, s = symbols("m s", positive=True)

res = parse_latex_lark(r"\sqrt{\frac{m^{2}}{s^{2}}}")

for symbol in res.free_symbols:
    try:
        units = u.find_unit(str(symbol))
        if units[0] == str(symbol):
            res = res.subs({ symbol: getattr(u, units[0])})
    except AttributeError:
        continue

print(res)
