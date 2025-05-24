from typing import Iterator
from lark import Token, Transformer, Discard, v_args
from sympy import *
import sympy
import sympy.parsing.latex.lark.transformer

@v_args(inline=True)
class FunctionsTransformer(Transformer):
    
    def _MULTIARG_FUNC_ARG_DELIMITER(self,_):
        return Discard
    
    def trig_function(self, func_token: Token, exponent: Expr | None, arg: Expr):
        exponent = 1 if exponent is None else exponent
        # TODO: should this use the type instead of the value?
        func_name = func_token.value
        
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
        
    def frac(self, numerator: Expr, denominator: Expr):
        return numerator * denominator**-1
    
    def binom(self, n: Expr, k: Expr):
        return binomial(n, k)
    
    def sqrt(self, degree: Expr | None, arg: Expr):
        if degree is None:
            return sqrt(arg)
        else:
            return root(arg, degree)
        
    def conjugate(self, arg: Expr):
        return conjugate(arg)

    def log_implicit_base(self, func_token: Token, exponent: Expr | None, arg: Expr):
        exponent = 1 if exponent is None else exponent
        
        log_type = func_token.type
            
        if log_type == 'FUNC_LOG' or log_type == 'FUNC_LN':
            return log(arg)**exponent
        elif log_type == 'FUNC_LG':
            return log(arg, 10)**exponent

    def log_explicit_base(self, _func_token: Token, base: Expr, exponent: Expr | None, arg: Expr):
        exponent = 1 if exponent is None else exponent
            
        return log(arg, base)**exponent
    
    def log_explicit_base_exponent_first(self, func_token: Token, exponent: Expr | None, base: Expr, arg: Expr):
        return self.log_explicit_base(func_token, base, exponent, arg)
    
    def exponential(self, exponent: Expr | None, arg: Expr):
        exponent = 1 if exponent is None else exponent
        
        return exp(arg)**exponent

    def factorial(self, arg: Expr):
        return factorial(arg)

    def limit(self, symbol: Expr, approach_value: Expr, direction: str | None, arg: Expr):
        direction = '+-' if direction is None else direction
        
        return limit(arg, symbol, approach_value, direction)
    

    def sum_start_iter_first(self, iter_symbol: Expr, start_iter: Expr, end_iter: Expr, expression: Expr):
        return Sum(expression, (iter_symbol, start_iter, end_iter))
    
    def sum_end_iter_first(self, end_iter: Expr, iter_symbol: Expr, start_iter: Expr, expression: Expr):
        return self.sum_start_iter_first(iter_symbol, start_iter, end_iter, expression)
    
    def product_start_iter_first(self, iter_symbol: Expr, start_iter: Expr, end_iter: Expr, expression: Expr):
        return Product(expression, (iter_symbol, start_iter, end_iter))
    
    def product_end_iter_first(self, end_iter: Expr, iter_symbol: Expr, start_iter: Expr, expression: Expr):
        return self.product_start_iter_first(iter_symbol, start_iter, end_iter, expression)
    
    def sign(self, sign_token: Token):
        return sign_token.value

    def abs(self, arg: Expr):
        return Abs(arg)
    
    def norm(self, arg: Expr):
        # only if scalar maybe?
        return Abs(arg)
    
    def floor(self, arg: Expr):
        return floor(arg)
    
    def ceil(self, arg: Expr):
        return ceiling(arg)
    
    def max(self, args: Iterator[Expr]):
        return Max(*args)
    
    def min(self, args: Iterator[Expr]):
        return Min(*args)
    
    def diff_symbol_exponent(self, symbol, exponent: Expr | None):
        return (symbol, 1 if exponent is None else exponent)
    
    def derivative_symbols_first(self, symbols: Iterator[tuple[Expr, Expr]], expr: Expr):
        return diff(expr, *symbols)
    
    @v_args(inline=False)
    def list_of_expressions(self, tokens: Iterator[Expr]):
        return list(filter(lambda x: not isinstance(x, Token) or x.type != 'COMMA', tokens))
        
