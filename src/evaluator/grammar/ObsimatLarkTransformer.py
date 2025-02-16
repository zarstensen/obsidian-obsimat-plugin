from grammar.ObsimatExpression import ObsimatExpression

from typing import Callable, Any, Self
from sympy.parsing.latex.lark.transformer import TransformToSymPyExpr
from sympy.parsing.latex.lark.latex_parser import LarkLaTeXParser
from sympy import *
from lark import Token, Transformer


# The ObsimatLarkTransofmer class provides functions for transforming
# rules defined in obsimat_grammar.lark into sympy expressions.
class ObsimatLarkTransformer(TransformToSymPyExpr):
   
    class latex_string:
        @staticmethod
        def visit_wrapper(f, data, children, meta):
            return ObsimatExpression(children[0], meta)

   
    def matrix_norm(self, tokens):
        return tokens[1].norm()

    def matrix_inner_product(self, tokens):
        return tokens[1].dot(tokens[3], hermitian=True, conjugate_convention='maths')

    def quick_derivative(self, tokens):
        if len(tokens[0].free_symbols) == 0:
            return S(0)
        else:
            return diff(tokens[0], list(tokens[0].free_symbols)[0], len(tokens[1]))
        
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
        return list(filter(lambda t: isinstance(t, ObsimatExpression), tokens))
    
    def align_rel(self, tokens):
        # just ignore the alignment characters
        return next(filter(lambda t: t.type != "MATRIX_COL_DELIM", tokens)) 
    
    def partial_relation(self,  tokens):
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
            
        relation_type = self._relation_token_to_type(relation_token)
        # these invalid relations just get a dummy variable to the side they miss a variable.
        if is_left == True:
            return relation_type(expression, Dummy())
        elif is_left == False:
            return relation_type(Dummy(), expression)
        
        raise ValueError("Invalid relation")
            
    
    class chained_relation:
        @staticmethod
        def visit_wrapper(f, data, children, meta):
            relation_type = f._relation_token_to_type(children[1])
            return [ ObsimatExpression(children[0], meta), ObsimatExpression(relation_type(children[0].rhs, children[2], meta))]
        
    def chained_relation(self, tokens):
        relation_type = self._relation_token_to_type(tokens[1])
        
        return [tokens[0], relation_type(tokens[0].rhs, tokens[2])]
        
    def _relation_token_to_type(self, token):
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