from itertools import combinations

from sympy import *
from sympy.logic.boolalg import as_Boolean


# SymbolicIff is an "extension" (functionality wise, not class wise) of the Equivalent (iff) function.
# It does the exact thing that Equivalent does, but if one of the args are not a boolean, it instead checks
# if all args equal each other.
# This does mean that this is technically not an Iff, as SymbolicIff evaluates to a True or False value if one of the args is not boolean,
# where it might make more sense to evaluate to a symbolic result.
# An example is SymbolicIff(2 * a, 2), here it will return False, because 2 * a != 2, for some values of a, but it is technically true for a = 1.
# Therefore this is more akin to a universal quantification combined with an iff in the symbolic case.
class SymbolicIff(Function):

    @classmethod
    def eval(cls, *args: Expr) -> Expr:
        try:
            args_bool = ( as_Boolean(arg) for arg in args)
            return Equivalent(*args_bool)
        except:
            simplified_args = [simplify(arg) for arg in args]
            return all(a.equals(b) for a, b in combinations(simplified_args, 2))
