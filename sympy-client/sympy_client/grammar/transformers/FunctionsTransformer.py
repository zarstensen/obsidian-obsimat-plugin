from typing import Iterator

import sympy
from lark import Token, Transformer, v_args
from sympy import *
from sympy.core.function import AppliedUndef
from sympy.tensor.array import derive_by_array
from sympy_client.grammar.SympyParser import DefinitionStore


# The FucntionsTransformer holds the implementation of various mathematical function rules,
# defined in the latex math grammar.
@v_args(inline=True)
class FunctionsTransformer(Transformer):
    
    def __init__(self, definitions_store: DefinitionStore):
        self.__definitions_store = definitions_store
    
    def trig_function(self, func_token: Token, exponent: Expr | None, arg: Expr) -> Expr:
        func_type = func_token.type.replace('FUNC_', '').lower()
        
        is_inverse = False
        
        if exponent == -1:
            exponent = 1
            is_inverse = not is_inverse
        
        if is_inverse:
            if func_type.startswith('a'):
                func_type = func_type[1:]
            else:
                func_type = 'a' + func_type

        # find func name in sympy module, the tokens are named after their sympy equivalents.
        trig_func = getattr(sympy, func_type)
        
        return self._try_raise_exponent(trig_func(arg), exponent)
        
    def frac(self, numerator: Expr, denominator: Expr) -> Expr:
        return numerator * denominator**-1
    
    def binom(self, n: Expr, k: Expr) -> Expr:
        return binomial(n, k)
    
    def sqrt(self, degree: Expr | None, arg: Expr) -> Expr:
        if degree is None:
            return sqrt(arg)
        else:
            return root(arg, degree)
        
    def conjugate(self, arg: Expr) -> Expr:
        return conjugate(arg)

    def log_implicit_base(self, func_token: Token, exponent: Expr | None, arg: Expr) -> Expr:
        log_type = func_token.type
        base = 10 if log_type == 'FUNC_LG' else None
        
        if base is not None:
            log_val = log(arg, base)
        else:
            log_val = log(arg)

        return self._try_raise_exponent(log_val, exponent)

    def log_explicit_base(self, _func_token: Token, base: Expr, exponent: Expr | None, arg: Expr) -> Expr:
        return self._try_raise_exponent(log(arg, base), exponent)
    
    def log_explicit_base_exponent_first(self, func_token: Token, exponent: Expr | None, base: Expr, arg: Expr) -> Expr:
        return self.log_explicit_base(func_token, base, exponent, arg)
    
    def exponential(self, exponent: Expr | None, arg: Expr) -> Expr:
        return self._try_raise_exponent(exp(arg), exponent)

    def factorial(self, arg: Expr) -> Expr:
        return factorial(arg)

    def limit(self, symbol: Expr, approach_value: Expr, direction: str | None, arg: Expr) -> Expr:
        # default direction of limits is both positive and negative.
        direction = '+-' if direction is None else direction
        return limit(arg, symbol, approach_value, direction)
    

    def sign(self, sign_token: Token) -> str:
        return sign_token.value

    def abs(self, arg: Expr) -> Expr:
        # if arg is a matrix, this notation actually means taking its determinant.
        if isinstance(arg, MatrixBase):
            return arg.det()
        
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
    
    def diff_symbol_arg_list(self, *arg_list: tuple[Expr, Expr]):
        return [*arg_list]
    
    def derivative_symbols_first(self, symbols: Iterator[tuple[Expr, Expr]], expr: Expr):
        return diff(expr, *symbols)
    
    def derivative_func_first(self, expr: Expr, symbols: Iterator[tuple[Expr, Expr]]):
        return self.derivative_symbols_first(symbols, expr)
    
    def derivative_prime(self, expr: Expr, primes: Token):
        
        symbols = expr.free_symbols
        
        if isinstance(expr, AppliedUndef):
            func_def = self.__definitions_store.get_function_definition(expr.func)
        
            if func_def is not None:
                symbols = func_def.args
                expr = func_def.get_body()
        
        if len(symbols) == 0:
            return S.Zero
        else:
            return diff(expr, sorted(symbols, key=str)[0], primes.value.count("'"), evaluate=False)
    
    def integral_no_bounds(self, expr: Expr | None, symbol: Expr):
        expr = 1 if expr is None else expr
        return integrate(expr, symbol)
    
    def integral_lower_bound_first(self, lower_bound: Expr, upper_bound: Expr, expr: Expr | None, symbol: Expr):
        expr = 1 if expr is None else expr
        return integrate(expr, (symbol, lower_bound, upper_bound))
    
    def integral_upper_bound_first(self, upper_bound: Expr, lower_bound: Expr, expr: Expr | None, symbol: Expr):
        return self.integral_lower_bound_first(lower_bound, upper_bound, expr, symbol)
    
    # Series Specific Implementations
    
    def sum_start_iter_first(self, iter_symbol: Expr, _: Token, start_iter: Expr, end_iter: Expr, expression: Expr) -> Expr:
        return Sum(expression, (iter_symbol, start_iter, end_iter))
    
    def sum_end_iter_first(self, end_iter: Expr, iter_symbol: Expr, separator: Token, start_iter: Expr, expression: Expr) -> Expr:
        return self.sum_start_iter_first(iter_symbol, separator, start_iter, end_iter, expression)
    
    def product_start_iter_first(self, iter_symbol: Expr, _: Token, start_iter: Expr, end_iter: Expr, expression: Expr) -> Expr:
        return Product(expression, (iter_symbol, start_iter, end_iter))
    
    def product_end_iter_first(self, end_iter: Expr, iter_symbol: Expr, separator: Token, start_iter: Expr, expression: Expr) -> Expr:
        return self.product_start_iter_first(iter_symbol, separator, start_iter, end_iter, expression)
    
    
    # Matrix Specific Implementations
    
    def norm(self, arg: Expr) -> Expr:
        return self._ensure_matrix(arg).norm()
    
    def inner_product(self, lhs: Expr, rhs: Expr) -> Expr:
        return self._ensure_matrix(lhs).dot(self._ensure_matrix(rhs), conjugate_convention='right')
    
    def determinant(self, exponent: Expr | None, mat: Expr) -> Expr:
        return self._try_raise_exponent(self._ensure_matrix(mat).det(), exponent)
    
    def trace(self, exponent: Expr | None, mat: Expr) -> Expr:
        return self._try_raise_exponent(self._ensure_matrix(mat).trace(), exponent)
    
    def adjugate(self, exponent: Expr | None, mat: Expr) -> Expr:
        return self._try_raise_exponent(self._ensure_matrix(mat).adjugate(), exponent)
    
    def rref(self, exponent: Expr | None, mat: Expr) -> Expr:
        return self._try_raise_exponent(self._ensure_matrix(mat).rref()[0], exponent)
    
    def exp_transpose(self, mat: Expr, exponent: Token) -> Expr:
        exponents_str = exponent.value
        exponents_str = exponents_str.replace('{', '').replace('}', '').replace('\\ast', 'H').replace('*', 'H').replace('\\prime', 'T').replace("'", 'T').replace(' ', '')
        
        for e in exponents_str:
            if e == 'T':
                mat = mat.transpose()
            elif e == 'H':
                mat = mat.adjoint()
            else:
                raise RuntimeError(f"Unexpected exponent: {e}")
        
        return mat
    
    # Linear Alg Specific Implementations
    
    def gradient(self, exponent: Expr | None, expr: Expr) -> Expr:
        symbols = list(sorted(expr.free_symbols, key=str))
        
        if isinstance(expr, Symbol):
            func_def = self.__definitions_store.get_function_definition(self.__definitions_store.deserialize_function(str(expr)))
            
            if func_def is not None:
                symbols = func_def.args
                expr = func_def.get_body()
        
        return self._try_raise_exponent(Matrix(derive_by_array(expr, symbols)), exponent)

    def hessian(self, exponent: Expr | None, expr: Expr) -> Expr:
        symbols = list(sorted(expr.free_symbols, key=str))
        
        if isinstance(expr, Symbol):
            func_def = self.__definitions_store.get_function_definition(self.__definitions_store.deserialize_function(str(expr)))
        
            if func_def is not None:
                symbols = func_def.args
                expr = func_def.get_body()
        
        return self._try_raise_exponent(hessian(expr, symbols), exponent)
        
    def jacobian(self, exponent: Expr | None, matrix: Expr) -> Expr:
        symbols = list(sorted(matrix.free_symbols, key=str))
        
        if isinstance(matrix, Symbol):
            func_def = self.__definitions_store.get_function_definition(self.__definitions_store.deserialize_function(str(matrix)))
        
            if func_def is not None:
                symbols = func_def.args
                matrix = func_def.get_body()
        
        matrix = self._ensure_matrix(matrix)
            
        if not matrix.rows == 1 and not matrix.cols == 1:
            raise ShapeError("Jacobian expects a single row or column vector")
        
        # sympy has a built in jacobian, but it does not have an evaluate option,
        # so we just do it manually here.
        
        gradients = []
        
        for item in matrix:
            gradients.append(Matrix([derive_by_array(item, symbols)]))
        
        return self._try_raise_exponent(Matrix.vstack(*gradients), exponent)
    
    # Helper Methods
    
    @v_args(inline=False)
    def list_of_expressions(self, tokens: Iterator[Expr]) -> list[Expr]:
        return list(filter(lambda x: not isinstance(x, Token) or x.type != 'COMMA', tokens))

    # tries to raise arg to the given exponent, exept if it is None,
    # or doing so results in no change to the resulting expression.
    def _try_raise_exponent(self, arg: Expr, exponent: Expr | None) -> Expr:
        if exponent is not None and exponent != 1:
            return pow(arg, exponent)
        else:
            return arg

    # If the given object is not a matrix, try to construct a 0d Matrix containing the given value.
    # If it is already a matrix, returns the matrix without modifying it in any way.
    def _ensure_matrix(self, obj: Basic) -> MatrixBase:
        if not hasattr(obj, "is_Matrix") or not obj.is_Matrix:
            return Matrix([obj])
        return obj
