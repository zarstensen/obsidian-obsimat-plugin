from lark import Transformer
from sympy import *

class ConstantsTransformer(Transformer):
    
    def CONST_PI(self, _tokens):
        return pi
    
    def CONST_EULER(self, _tokens):
        return E
    
    def CONST_IMAGINARY(self, _tokens):
        return I
    
    def CONST_INFINITY(self, _tokens):
        return oo
