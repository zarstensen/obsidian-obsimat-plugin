from grammar.ObsimatLatexParser import ObsimatLatexParser
from modes.SolveMode import solveMode
from tests.TestResponse import TestResponse
import asyncio

from sympy import *

class TestSolve:
    parser = ObsimatLatexParser()
    
    def test_solve_with_domain(self):
        x = symbols('x')
        
        response = TestResponse()
        asyncio.run(solveMode({ "expression": r"\sin(x) = 0", "environment": { "domain": "Interval.Ropen(0, 2 * pi)"} }, response, self.parser))
        assert response.hasResult()
        
        assert response.getResult()['result']['symbol'] == x
        assert response.getResult()['result']['solution'] == FiniteSet(0, pi)