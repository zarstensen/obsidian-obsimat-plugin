from lark import Token, Transformer
from sympy import *
import sympy

class FunctionsTransformer(Transformer):
    def trig_function(self, tokens):
        func_name = tokens[0]
        # remove the slash before the name
        func_name = func_name.replace('\\', '').replace('arc', 'a').replace('ar', 'a')
        
        # find func name in sympy module
        func = getattr(sympy, func_name)
        
        if len(tokens) == 4:
            assert tokens[1].type == 'CARET'
            # TODO: handle if exponent is -1, then it should be the inverse of the function
            return func(tokens[3])**tokens[2]
        elif len(tokens) == 2:
            return func(tokens[1])
        else:
            raise RuntimeError("Unexpected amount of tokens received")
        
    def frac(self, tokens):
        return tokens[1] * tokens[2]**-1