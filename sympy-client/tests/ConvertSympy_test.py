from sympy_client.grammar.LatexCompiler import LatexSympyCompiler, LatexSympySymbolsCompiler
from sympy_client.command_handlers.ConvertSympyHandler import *

from sympy import *

## Tests the conver to sympy mode.
class TestConvertSympy:
    expr_compiler = LatexSympyCompiler
    symbols_compiler = LatexSympySymbolsCompiler
    
    def test_convert_simple(self):
        a, b = symbols("a b")
        
        handler = ConvertSympyHandler(self.expr_compiler, self.symbols_compiler)
        
        result = handler.handle({"expression": "a + b + x + y", "environment": { "variables": {
            'x': '25',
            'y': '50'
        }}})

        assert result.sympy_expr == a + b
