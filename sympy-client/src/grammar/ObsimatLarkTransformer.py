from grammar.SystemOfExpr import SystemOfExpr
from grammar.CachedSymbolSubstitutor import CachedSymbolSubstitutor
from grammar.FunctionSubstitutor import FunctionSubstitutor

from sympy.parsing.latex.lark.transformer import TransformToSymPyExpr
from sympy.core.relational import Relational
from sympy import *
from lark import Token, Discard


# The ObsimatLarkTransofmer class provides functions for transforming
# rules defined in obsimat_grammar.lark into sympy expressions.
class ObsimatLarkTransformer(TransformToSymPyExpr):

    SYMBOL_CREATION_METHODS = [
        'SYMBOL',
        'GREEK_SYMBOL_WITH_PRIMES',
        'LATIN_SYMBOL_WITH_LATIN_SUBSCRIPT',
        'GREEK_SYMBOL_WITH_LATIN_SUBSCRIPT',
        'LATIN_SYMBOL_WITH_GREEK_SUBSCRIPT',
        'GREEK_SYMBOL_WITH_GREEK_SUBSCRIPT',
        'multi_letter_symbol',
        'symbol_prime',
        'ext_multi_letter_symbol'
        ]

    # Constructs an ObsimatLarkTransformer.
    def __init__(self, symbol_substitutor: CachedSymbolSubstitutor, function_substitutor: FunctionSubstitutor):
        super().__init__()
        self._symbol_substitutor = symbol_substitutor
        self._function_substitutor = function_substitutor
        
        # wrap all symbol rules and terminal handlers in a method which attempts to 
        # substitute the symbol for a variable defined in the given environment.
        for symbol_method in self.SYMBOL_CREATION_METHODS:
            symbol_transform = getattr(self, symbol_method)
            setattr(self, symbol_method, lambda tokens, symbol_transform=symbol_transform: self._try_substitute(symbol_transform, tokens))
    
    # tries to substitute the symbol returned form the symbol_transform callable, with a variable defined in the environment.
    # if there is no such variable, the symbol is returned as is.
    def _try_substitute(self, symbol_transform, tokens):
        symbol = symbol_transform(tokens)
        
        substituted_value = self._symbol_substitutor.get_symbol_substitution(str(symbol)) or self._symbol_substitutor.get_symbol_substitution(f"\\{str(symbol)}")
        
        if substituted_value is not None:
            return substituted_value
        else:
            return symbol

    def function_applied(self, tokens):
        # try to substitute function
        function = self._function_substitutor.get_function_substitution(str(tokens[0]), list(tokens[2]))
        
        if function is None:
            return super().function_applied(tokens)
        else:
            return function

    def whitespace(self, _tokens):
        return Discard

    def ext_multi_letter_symbol(self, tokens):
        return Symbol(tokens[0])

    def matrix_norm(self, tokens):
        with evaluate(True):
            return tokens[1].doit().norm()

    def matrix_inner_product(self, tokens):
        with evaluate(True):
            return tokens[1].doit().dot(tokens[3].doit(), hermitian=True, conjugate_convention="right")

    def gradient(self, tokens):
        return self._expr_gradient(tokens[1], tokens[1].free_symbols)

    def hessian(self, tokens):

        symbols = list(sorted(tokens[1].free_symbols, key=str))
        
        return Matrix([
            [
                diff(tokens[1], symbol_col, symbol_row, evaluate=False) for symbol_col in symbols
            ] for symbol_row in symbols
        ])
        
    def jacobian(self, tokens):
        matrix = tokens[1]
        
        if not self._obj_is_sympy_Matrix(matrix):
            matrix = Matrix([matrix])
            
        if not matrix.rows == 1 and not matrix.cols == 1:
            raise ShapeError("Jacobian expects a single row or column vector")
        
        # sympy has a built in jacobian, but it does not have an evaluate option,
        # so we just do it manually here.
        
        gradients = []
        
        for item in matrix:
            gradients.append(self._expr_gradient(item, matrix.free_symbols))
        
        return Matrix.vstack(*gradients)
      
    def rref(self, tokens):
        if not self._obj_is_sympy_Matrix(tokens[1]):
            raise ValueError("RREF expects a matrix")
        
        return tokens[1].rref()[0]

    def quick_derivative(self, tokens):
        if len(tokens[0].free_symbols) == 0:
            return S(0)
        else:
            return diff(tokens[0], sorted(tokens[0].free_symbols, key=str)[0], len(tokens[1]), evaluate=False)

    def math_constant(self, tokens):
        match str(tokens[0]):
            case "\\pi":
                return S.Pi
            case "\\tau":
                return 2 * S.Pi
            case "e":
                return S.Exp1
            case "i":
                return I
            case _:
                raise ValueError("Unknown mathematical constant")

    def system_of_expressions(self, tokens):
        return SystemOfExpr(list(filter(lambda t: not isinstance(t, Token), tokens)))

    class system_of_expressions_expr:
        @staticmethod
        def visit_wrapper(f, data, children, meta):
            # location adata is needed for system_of_expressions handler.
            return (children[0], meta)

    def align_rel(self, tokens):
        # just ignore the alignment characters
        return next(filter(lambda t: t.type != "MATRIX_COL_DELIM", tokens))

    def partial_relation(self, tokens):
        relation_token = None
        expression = None
        is_left = None
        if isinstance(tokens[0], Token):
            relation_token = tokens[0]
            expression = tokens[1]
            is_left = False
        else:
            relation_token = tokens[1]
            expression = tokens[0]
            is_left = True

        relation_type = ObsimatLarkTransformer._relation_token_to_type(relation_token)
        # these invalid relations just get a dummy variable to the side they miss a variable.
        if is_left == True:
            return relation_type(expression, Dummy())
        elif is_left == False:
            return relation_type(Dummy(), expression)

        raise ValueError("Invalid relation")

    class chained_relation:
        @staticmethod
        def visit_wrapper(f, data, children, meta):
            relation_type = ObsimatLarkTransformer._relation_token_to_type(children[1])

            relation = children[0]
            
            if isinstance(relation, Relational):
                return SystemOfExpr(
                    [
                        (children[0], meta),
                        (relation_type(children[0].rhs, children[2], evaluate=False), meta),
                    ]
                )
            elif isinstance(relation, SystemOfExpr):
                return relation.extend([ (relation_type(relation.get_expr(-1).rhs, children[2], evaluate=False), meta) ])
            else:
                raise ValueError("Chained relation must be between a sympy relation or a system of expressions, where the last expression is a relation.")

    @staticmethod
    def _relation_token_to_type(token):
        match token.type:
            case "EQUAL":
                return Eq
            case "NOT_EQUAL":
                return Ne
            case "LT":
                return Lt
            case "LTE":
                return Le
            case "GT":
                return Gt
            case "GTE":
                return Ge
            case _:
                raise ValueError("Invalid relation token")
            
    def eq(self, tokens):
        return Eq(tokens[0], tokens[2], evaluate=False)
    
    def ne(self, tokens):
        return Ne(tokens[0], tokens[2], evaluate=False)

    def lt(self, tokens):
        return Lt(tokens[0], tokens[2], evaluate=False)
    
    def lte(self, tokens):
        return Le(tokens[0], tokens[2], evaluate=False)
    
    def gt(self, tokens):
        return Gt(tokens[0], tokens[2], evaluate=False)
    
    def gte(self, tokens):
        return Ge(tokens[0], tokens[2], evaluate=False)
    
    @staticmethod
    def _expr_gradient(expression: Expr, free_symbols):
        return Matrix([ [ diff(expression, symbol, evaluate=False) for symbol in sorted(free_symbols, key=str)] ])
