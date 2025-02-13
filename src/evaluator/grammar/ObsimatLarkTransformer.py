from sympy.parsing.latex.lark.transformer import TransformToSymPyExpr
from sympy import *

# The ObsimatLarkTransofmer class provides functions for transforming
# rules defined in obsimat_grammar.lark into sympy expressions.
class ObsimatLarkTransformer(TransformToSymPyExpr):

    def matrix_norm(self, tokens):
        return sqrt(tokens[1].dot(tokens[1], hermitian=True, conjugate_convention='maths'))

    def matrix_inner_product(self, tokens):
        return tokens[1].dot(tokens[3], hermitian=True, conjugate_convention='maths')

    def quick_derivative(self, tokens):
        if len(tokens[0].free_symbols) == 0:
            return 0
        else:
            return diff(tokens[0], list(tokens[0].free_symbols)[0], len(tokens[1]))
        
    def math_constant(self, tokens):
        match str(tokens[0]):
            case "\\pi":
                return S.Pi
            case "\\tau":
                return 2 * S.Pi
            case "e":
                return S.Exp1
            case _:
                raise ValueError("Unknown mathematical constant")
