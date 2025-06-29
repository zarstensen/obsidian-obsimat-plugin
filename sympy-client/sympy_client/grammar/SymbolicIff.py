from itertools import combinations

from sympy import *
from sympy.logic.boolalg import as_Boolean


class SymbolicIff(Function):

    @classmethod
    def eval(cls, *args: Expr) -> Expr:
        try:
            args_bool = ( as_Boolean(arg) for arg in args)
            return Equivalent(*args_bool)
        except:
            simplified_args = [simplify(arg) for arg in args]
            return all(a.equals(b) for a, b in combinations(simplified_args, 2))
