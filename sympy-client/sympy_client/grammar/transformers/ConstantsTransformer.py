from lark import Transformer, v_args
from sympy import *

@v_args(inline=True)
class ConstantsTransformer(Transformer):
    
    def CONST_PI(self, _):
        return pi
    
    def CONST_EULER(self, _):
        return E
    
    def CONST_IMAGINARY(self, _):
        return I
    
    def CONST_INFINITY(self, _):
        return oo
