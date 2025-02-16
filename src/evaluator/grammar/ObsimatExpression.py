from sympy import Expr
from lark.tree import Meta 

class ObsimatExpression:
    def __init__(self, sympy_expression: Expr, location_metadata: Meta):
        self.__sympy_expression = sympy_expression
        self.__location_metadata = location_metadata
        
    def sympy_expr(self) -> Expr:
        return self.__sympy_expression
    
    def location(self) -> Meta:
        return self.__location_metadata