from sympy import *
import re

# The default formatter used to conver the results of a mode handler,
# into a displayable string.
# simply converts the given expression to latex, and remove any text formatting.
# TODO: this should probably be a custom sympy printer in the future
def sympy_expr_to_latex(sympy_expr: Expr) -> str:
        # Sympy sometimes errors out when trying to convert a sympy expression to a string,
        # when evaluate is set to false, so here it is forced to always be true.
        with evaluate(True):
            return re.sub(r"\\text\{(.*?)\}", r"\1", latex(sympy_expr))
