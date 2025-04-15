from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.modes.ConvertSympyMode import convert_sympy_handler
from tests.MockResponse import MockResponse
import asyncio

from sympy import *


## Tests the conver to sympy mode.
class TestConvertSympy:
    parser = ObsimatLatexParser()
    
    def test_convert_simple(self):
        a, b = symbols("a b")
        
        response = MockResponse()
        asyncio.run(convert_sympy_handler({"expression": "a + b", "environment": {}}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()
            
        with evaluate(False):
            assert result['result'] == a + b
