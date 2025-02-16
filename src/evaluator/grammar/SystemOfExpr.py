from lark.tree import Meta 

from typing import Callable, Any

# The SystemOfExpr class represents a list of sympy expressions and their original locations in some source text.
class SystemOfExpr:
    def __init__(self, expressions: list[tuple[Any, Meta]]):
        self.__expressions: list[Any] = [ e[0] for e in expressions]
        self.__location_data: list[Meta] = [ e[1] for e in expressions ]
    
    # retreive number of expressions in the system
    def __len__(self):
        return len(self.__expressions)
    
    # modify a single expression in the system.
    def change_expr(self, expression_index: int, change_func: Callable[[Any], Any]):
        self.__expressions[expression_index] = change_func(self.__expressions[expression_index])
    
    # retreive the expression at the given index
    def get_expr(self, expression_index: int):
        return self.__expressions[expression_index]
    
    # retreive all expressions
    def get_all_expr(self):
        return tuple(self.__expressions)
    
    # retreive location information about the given expression
    def get_location(self, expression_index: int) -> Meta:
        return self.__location_data[expression_index]
    
    # retreive all location information.
    def get_all_locations(self):
        return tuple(self.__location_data)