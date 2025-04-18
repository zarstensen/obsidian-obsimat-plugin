from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.command_handlers.ConvertSympyHandler import *

from sympy import *

## Tests the conver to sympy mode.
class TestConvertSympy:
    parser = ObsimatLatexParser()
    
    def test_convert_simple(self):
        a, b = symbols("a b")
        
        handler = ConvertSympyHandler(self.parser)
        
        result = handler.handle({"expression": "a + b", "environment": {}})

        assert result.sympy_expr == a + b
