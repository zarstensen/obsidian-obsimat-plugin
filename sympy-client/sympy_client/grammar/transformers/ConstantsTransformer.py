from lark import Transformer, v_args
from sympy import *


# This transformer is responsible for providing the values of various mathematical constants.
@v_args(inline=True)
class ConstantsTransformer(Transformer):
    def CONST_PI(self, _) -> Expr:
        return pi
    
    def CONST_EULER(self, _) -> Expr:
        return E
    
    def CONST_IMAGINARY(self, _) -> Expr:
        return I
    
    def CONST_INFINITY(self, _) -> Expr:
        return oo
