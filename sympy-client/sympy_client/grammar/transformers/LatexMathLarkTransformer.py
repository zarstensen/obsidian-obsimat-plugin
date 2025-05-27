import itertools
from enum import Enum
from typing import Iterator

import sympy_client.UnitsUtils as UnitUtils
from lark import Token, v_args
from sympy import *
from sympy.core.numbers import Float, Integer
from sympy.core.operations import LatticeOp
from sympy.logic.boolalg import *
from sympy.physics.units import Quantity

from ..CachedSymbolSubstitutor import CachedSymbolSubstitutor
from ..FunctionStore import FunctionStore
from ..SystemOfExpr import SystemOfExpr
from .ConstantsTransformer import ConstantsTransformer
from .FunctionsTransformer import FunctionsTransformer


# Specialized And class, which does not change the order,
# or remove equal expressions during construction.
class ChainedRelation(And):
    
    @classmethod
    def _new_args_filter(cls, args):
        args = BooleanFunction.binary_check_and_simplify(*args)
        args = LatticeOp._new_args_filter(args, And)
        return args

# The LatexMathLarkTransofmer class provides functions for transforming
# rules defined in latex_math_grammar.lark into sympy expressions.
class LatexMathLarkTransformer(ConstantsTransformer, FunctionsTransformer):

    class Delim(Enum):
        MatDelim = 1

    def __init__(self, symbol_substitutor: CachedSymbolSubstitutor, function_store: FunctionStore):
        super().__init__()
        self._symbol_substitutor = symbol_substitutor
        self._function_store = function_store
    
    @v_args(inline=True)
    def NUMERIC_DIGIT(self, digit: Token):
        return Integer(str(digit))
    
    @v_args(inline=True)
    def NUMERIC_NUMBER(self, number: Token):
        
        number_str = str(number)
        
        if '.' in number_str:
            return Float(number_str)
        return Integer(number_str)

    def system_of_relations(self, relations: list[Expr]) -> SystemOfExpr:
        return SystemOfExpr([
            next(row) # the row iterator should only contain 1 element
            for is_delim, row in itertools.groupby(relations, lambda t: t == self.Delim.MatDelim)
            if not is_delim
            ])

    class system_of_relations_expr:
        @staticmethod
        def visit_wrapper(_f, _data, children, meta) -> tuple[Expr]:
            # location data is needed for system_of_expressions handler.
            return (children[0], meta)

    def relation(self, tokens: list[Expr|Token]) -> ChainedRelation | Expr:
        if len(tokens) == 1:
            return tokens[0]

        # construct a list of relations which later will be used to construct
        # a chained relation object.
        # a = b = c should produce [a = b, b = c],
        # that way when we chain them with and's (a = b & b = c),
        # it should be logically equivalent to a = b = c
        prev_expr = Dummy()
        relation_type = None
        
        relations = []
        
        for token in tokens:
            if isinstance(token, Token):
                relation_type = token.type
            else:
                if relation_type is not None:
                    relations.append(self._create_relation(prev_expr, token, relation_type))
                    relation_type = None
                prev_expr = token
                
        if relation_type is not None:
            relations.append(self._create_relation(prev_expr, Dummy(), relation_type))
        
        print(relations)
        
        if len(relations) == 1:
            return relations[0]
        else:
            return ChainedRelation(*relations, evaluate=False)

    def expression(self, tokens: list[Expr|Token]) -> Expr:
        # construct a sum between the given sympy expressions,
        # with the sign that separates them in the tokens list.
        
        signs = [ self.SIGN_DICT[t.type] for t in filter(lambda t: isinstance(t, Token), tokens)]
        values = list(filter(lambda t: not isinstance(t, Token), tokens))
        
        # if no first sign was specified, it is implicitly '+'.
        if len(signs) < len(values):
            signs.insert(0, self.SIGN_DICT['ADD']) 
        
        if len(signs) != len(values):
            raise RuntimeError(f"Error, too few signs were present in expression, expected {len(values) - 1} - {len(values)} got {len(signs)}")
        
        result = signs[0] * values[0]
        
        # TODO: perhaps scalars should be autoconverted to 0d matrices here,
        # if it is attempted to sum a matrix and a scalar.
        for sign, value in zip(signs[1:], values[1:]):
            result += sign * value
        
        return result
    
    def term(self, tokens: list[Expr|Token]) -> Expr:
        # multiply / divide a series of factor together.
        # tokens is a list of sympy expressions, representing factors,
        # separated by a multiplication / division token.
        
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
    
    def implicit_multiplication(self, factors: list[Expr]) -> Expr:
        result = S.One
        
        for token in factors:
            result *= token
        
        return result
    
    @v_args(inline=True)
    def exponentiation(self, base: Expr, exponent: Expr) -> Expr:
        # special matrix notation.
        if isinstance(exponent, Symbol) and hasattr(base, "is_Matrix") and base.is_Matrix:
            if str(exponent) == "T":
                return base.transpose()
            elif str(exponent) == "H":
                return base.adjoint()
            
        return pow(base, exponent)
    
    @v_args(inline=True)
    def symbol(self, *symbol_strings: str) -> Symbol:
        return Symbol(''.join(map(str,symbol_strings)))
    
    @v_args(inline=True)
    def substitute_symbol(self, symbol: Symbol) -> Symbol | Expr:
        substituted_value = self._symbol_substitutor.get_symbol_substitution(str(symbol))
        
        if substituted_value is not None:
            return substituted_value
        else:
            return symbol
    
    @v_args(inline=True)
    def undefined_function(self, func_name: Token, func_args: Iterator[Expr]) -> Function | Expr:
        func_name = func_name.value[:-1] # remove the suffixed parenthesees
        # TODO: workaround for now, the function store should be based on strings and not symbols.
        if Symbol(func_name) in self._function_store:
            return self._function_store[Symbol(func_name)].call(*func_args)
        else:
            return Function(func_name)(*func_args)
    
    @v_args(inline=True)
    def indexed_symbol(self, symbol: Expr, index: Expr | str, primes: str | None) -> Symbol:
        primes = '' if primes is None else primes
        indexed_text = str(index)
        
        if not indexed_text.startswith('{') or not indexed_text.endswith('}'):
            indexed_text = f"{{{indexed_text}}}"
        
        return self.symbol(f"{symbol}_{indexed_text}{primes}")
    
    @v_args(inline=True)
    def formatted_symbol(self, formatter: Token, text: str, primes: str | None) -> Symbol:
        formatter_text = str(formatter)
        primes = '' if primes is None else primes
        
        return self.symbol(f"{formatter_text}{text}{primes}")

    def brace_surrounded_text(self, tokens):        
        return ''.join(map(str, tokens))
    
    @v_args(inline=True)
    def unit(self, unit_symbol: Symbol) -> Quantity | Symbol:
        unit = UnitUtils.str_to_unit(str(unit_symbol))
        
        if unit is not None:
            return unit
        else:
            return self.symbol(unit_symbol)
    
    @v_args(inline=True)
    def matrix_body(self, *body: Expr | Token) -> list[list[Expr]]:
        return [
            list(row)
            for is_delim, row in itertools.groupby(body, lambda t: t == self.Delim.MatDelim)
            if not is_delim
        ]
    
    @v_args(inline=True)
    def matrix(self, matrix_begin_cmd, matrix_body, matrix_end_cmd) -> Matrix:
        return Matrix(matrix_body)
    
    @v_args(inline=True)
    def array_matrix(self, matrix_begin_cmd, array_options, matrix_body, matrix_end_cmd) -> Matrix:
        return Matrix(matrix_body)
    
    @v_args(inline=True)
    def det_matrix(self, _begin, matrix_body, _end) -> Matrix:
        return self.matrix(_begin, matrix_body, _end).det()
    
    def matrix_like_delim(self, _: Iterator[Token]):
        return self.Delim.MatDelim
    
    SIGN_DICT = {
        'ADD': S.One,
        'SUB': S.NegativeOne
    }
    
    def _create_relation(self, left: Expr, right: Expr, relation_type: str) -> Rel:
        with evaluate(False):
            match relation_type:
                case 'EQUAL':
                    return Eq(left, right, evaluate=False)
                case 'NOT_EQUAL':
                    return Ne(left, right)
                case 'LT':
                    return Lt(left, right)
                case 'LTE':
                    return Le(left, right)
                case 'GT':
                    return Gt(left, right)
                case 'GTE':
                    return Ge(left, right)
                case _:
                    raise RuntimeError(f"Unknown relation type '{relation_type}' between {left} and {right}")
