from sympy import *
from sympy_client.command_handlers.ConvertSympyHandler import *
from sympy_client.grammar.LatexParser import LatexParser


## Tests the conver to sympy mode.
class TestConvertSympy:
    parser = LatexParser()

    def test_convert_simple(self):
        a, b = symbols("a b")

        handler = ConvertSympyHandler(self.parser)

        result = handler.handle({"expression": "a + b", "environment": {}})

        assert result.sympy_expr == a + b
