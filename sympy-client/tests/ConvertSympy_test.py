from grammar.ObsimatLatexParser import ObsimatLatexParser
from tests.TestResponse import TestResponse
from modes.ConvertSympyMode import convert_sympy_handler
import asyncio

from sympy import *


## Tests the conver to sympy mode.
class TestConvertSympy:
    parser = ObsimatLatexParser()
    
    def test_convert_simple(self):
        a, b = symbols("a b")
        
        response = TestResponse()
        asyncio.run(convert_sympy_handler({"expression": "a + b", "environment": {}}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()
            
        with evaluate(False):
            assert result['result'] == a + b
