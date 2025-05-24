from typing import Iterator
from sympy_client.grammar.CachedSymbolSubstitutor import CachedSymbolSubstitutor
from sympy_client.grammar.FunctionStore import FunctionStore

from sympy.parsing.latex.lark.transformer import TransformToSymPyExpr
from .ConstantsTransformer import ConstantsTransformer
from .FunctionsTransformer import FunctionsTransformer
from sympy.core.operations import LatticeOp
from sympy.core.relational import Relational
from sympy.logic.boolalg import *
from sympy import *
from sympy.core.numbers import Integer, Float
from lark import Token, Discard, v_args

class ChainedRelation(And):
    
    @classmethod
    def _new_args_filter(cls, args):
        args = BooleanFunction.binary_check_and_simplify(*args)
        args = LatticeOp._new_args_filter(args, And)
        return args
    

# The ObsimatLarkTransofmer class provides functions for transforming
# rules defined in obsimat_grammar.lark into sympy expressions.
class ObsimatLarkTransformer(ConstantsTransformer, FunctionsTransformer):

    # Constructs an ObsimatLarkTransformer.
    def __init__(self, symbol_substitutor: CachedSymbolSubstitutor, function_store: FunctionStore):
        super().__init__()
        self._symbol_substitutor = symbol_substitutor
        self._function_store = function_store

    # sum a list of terms in an expression together
    def expression(self, tokens):
        
        signs = [ self.SIGN_DICT[t.type] for t in filter(lambda t: isinstance(t, Token), tokens)]
        values = list(filter(lambda t: not isinstance(t, Token), tokens))
        
        # if no first sign was specified, it is implicitly positive.
        if len(signs) < len(values):
            signs.insert(0, self.SIGN_DICT['ADD']) 
        
        if len(signs) != len(values):
            raise RuntimeError(f"Error, too few signs were present in expression, expected {len(values) - 1} - {len(values)} got {len(signs)}")
        
        result = S.Zero
        
        for sign, value in zip(signs, values):
            result += sign * value
        
        return result
    
    # multiply / divide a series of factor together
    def term(self, tokens):
        result = tokens[0]
        
        i = 1
        while i < len(tokens):
            operator = tokens[i]
            
            i += 1
            
            sign = S.One
            
            if isinstance(tokens[i], Token):
                sign = self.SIGN_DICT[tokens[i].type]
                i += 1
            
            factor = tokens[i]
            i += 1
            
            if operator.type == 'OPERATOR_MUL':
                result *= sign * factor
            elif operator.type == 'OPERATOR_DIV':
                result /= sign * factor
            else:
                raise RuntimeError(f"Unknown term operator '{operator.type}'")
        
        return result
    
    def implicit_multiplication(self, factors: Iterator[Expr]):
        result = S.One
        
        for token in factors:
            result *= token
        
        return result
    
    @v_args(inline=True)
    def exponentiation(self, base: Expr, exponent: Expr):        
        return base ** exponent
    
    @v_args(inline=True)
    def symbol(self, *symbol_strings: str):
        return Symbol(''.join(map(str,symbol_strings)))
    
    @v_args(inline=True)
    def indexed_symbol(self, symbol: Expr, index: Expr | str, primes: str | None):
        primes = '' if primes is None else primes
        indexed_text = str(index)
        
        if not indexed_text.startswith('{') or not indexed_text.endswith('}'):
            indexed_text = f"{{{indexed_text}}}"
        
        return f"{symbol}_{indexed_text}{primes}"
    
    @v_args(inline=True)
    def formatted_symbol(self, formatter: Token, text: str, primes: str | None):
        formatter_text = str(formatter)
        primes = '' if primes is None else primes
        
        return f"{formatter_text}{text}{primes}"
            
    
    def brace_surrounded_text(self, tokens):        
        return ''.join(map(str, tokens))
    
    # TODO: how does sympy do it?
    @v_args(inline=True)
    def NUMERIC_DIGIT(self, digit: Token):
        return Integer(str(digit))
    
    @v_args(inline=True)
    def NUMERIC_NUMBER(self, number: Token):
        
        number_str = str(number)
        
        if '.' in number_str:
            return Float(number_str)
        return Integer(number_str)
    
    @v_args(inline=True)
    def unit(self, unit_symbol: Token):
        return self.symbol(unit_symbol)
    
    SIGN_DICT = {
        'ADD': S.One,
        'SUB': S.NegativeOne
    }