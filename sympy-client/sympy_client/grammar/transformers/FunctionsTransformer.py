from lark import Token, Transformer, Discard
from sympy import *
import sympy
import sympy.parsing.latex.lark.transformer

class FunctionsTransformer(Transformer):
    
    def MULTIARG_FUNC_ARG_DELIMITER(self,_):
        return Discard
    
    def trig_function(self, tokens):
        exponent = 1
        arg = None
        
        if len(tokens) == 4:
            assert tokens[1].type == 'CARET'
            exponent = tokens[2]
            arg = tokens[3]
        else:
            arg = tokens[1]
        
        func_name = str(tokens[0])
        
        is_hyperbolic = func_name.endswith('h')
        is_inverse = func_name.startswith('\\a')
        
        name_length = 4 if is_hyperbolic else 3
        func_name = func_name[-name_length:]
        
        if exponent == -1:
            exponent = 1
            is_inverse = not is_inverse
        
        # construct func name from information.
            
        if is_inverse:
            func_name = 'a' + func_name
            
        # find func name in sympy module
        trig_func = getattr(sympy, func_name)
        
        return trig_func(arg)**exponent
        
    def frac(self, tokens):
        return tokens[1] * tokens[2]**-1
    
    def binom(self, tokens):
        return binomial(tokens[1], tokens[2])
    
    def sqrt(self, tokens):
        assert len(tokens) == 2 or len(tokens) == 3
        
        if len(tokens) == 2:
            return sqrt(tokens[1])
        elif len(tokens) == 3:
            return root(tokens[2], tokens[1])
        
    def conjugate(self, tokens):
        return conjugate(tokens[1])

    def log_implicit_base(self, tokens):
        exponent = 1
        arg = None
        
        if len(tokens) == 4:
            exponent = tokens[2]
            arg = tokens[3]
        else:
            arg = tokens[1]
            
        log_type = tokens[0].type
            
        if log_type == 'FUNC_LOG' or log_type == 'FUNC_LN':
            return log(arg)**exponent
        elif tokens[0].type == 'FUNC_LG':
            return log(arg, 10)**exponent

    def log_explicit_base(self, tokens):
        base = tokens[2]
        
        exponent = 1
        arg = None
        
        if len(tokens) == 6:
            exponent = tokens[4]
            arg = tokens[5]
        else:
            arg = tokens[3]
            
        return log(arg, base)**exponent
    
    def exponential(self, tokens):
        exponent = 1
        arg = None
        
        if len(tokens) == 4:
            exponent = tokens[2]
            arg = tokens[3]
        else:
            arg = tokens[1]
        
        return exp(arg)**exponent

    def factorial(self, tokens):
        return factorial(tokens[0])

    def limit(self, tokens):
        symbol = tokens[3]
        approach_value = tokens[5]
        
        direction = '+-'
        expression = None
        
        if len(tokens) == 10:
            direction = tokens[7].value
            expression = tokens[9]
        else:
            expression = tokens[7]
            
        return limit(expression, symbol, approach_value, direction)
        
    def sign(self, tokens):
        return tokens[0]

    def abs(self, tokens):
        return Abs(tokens[1])
    
    def norm(self, tokens):
        # only if scalar maybe?
        return Abs(tokens[1])
    
    def floor(self, tokens):
        return floor(tokens[1])
    
    def ceil(self, tokens):
        return ceiling(tokens[1])
    
    def max(self, tokens):
        return Max(*tokens[2])
    
    def min(self, tokens):
        return Min(*tokens[2])
    
    def list_of_expressions(self, tokens):
        return list(filter(lambda x: not isinstance(x, Token) or x.type != 'COMMA', tokens))
        
