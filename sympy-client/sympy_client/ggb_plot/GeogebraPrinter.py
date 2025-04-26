from sympy.printing.str import StrPrinter
from sympy import Equality
from sympy.core.function import Function, DefinedFunction
from sympy.core.relational import Relational
from sympy import MatrixBase


# The GeogebraPrinterClass converts a sympy expression to a geogebra parseble expression.
#
# This is an experimental class, and relies heavily on geogebras gracefull parser,
# but not all functions or data structures are guaranteed to actually be parsable by geogebra.
#
class GeogebraPrinter(StrPrinter):
    
    def _print_Function(self, expr: Function):
        func_name = expr.func.__name__
        
        # all geogebra math functions are with lower case,
        # but some sympy ones (like Abs) start with an uppercase letter.
        # this is corrected here.
        if isinstance(expr, DefinedFunction):
            func_name = func_name.lower()
        
        return f"{func_name}({','.join((self.doprint(a) for a in expr.args))})"
    
    def _print_Relational(self, expr: Relational):
        if isinstance(expr, Equality):
            op_str = '='
        else: 
            op_str = expr.rel_op
        
        return f"({self.doprint(expr.lhs)}) {op_str} ({self.doprint(expr.rhs)})"
    
    def _print_MatrixBase(self, expr: MatrixBase):
        # make all vectors be row vectors
        if expr.rows == 1:
            expr = expr.T
            
        # special case for vectors, they should be printed with parenthesees.
        if expr.cols == 1:
            return f"({','.join((self.doprint(value) for value in expr.iter_values()))})"
        
        return f"{{{
            ','.join((
                f"{{{
                    ','.join((self.doprint(value) for value in row))
                }}}" for row in expr.tolist()
            ))}}}"

def print_geogebra(expr):
    return GeogebraPrinter().doprint(expr)
    