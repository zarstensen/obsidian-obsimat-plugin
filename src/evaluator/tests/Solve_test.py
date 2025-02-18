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
        
        assert response.getResult()['result']['symbols'] == [x]
        assert response.getResult()['result']['solution'] == FiniteSet(0, pi)
        
    def test_solve_soe(self):
        x = symbols('x')
        
        response = TestResponse()
        
        asyncio.run(solveMode({ "expression": r"""
            \begin{align}
            x + y + z & = 5 \\
            2x + 5z & = 10 \\
            2y + x & = 3 \\
            \end{align}
            """, "environment": { } }, response, self.parser))
        
        assert response.hasResult()
        
        assert response.getResult()['result']['solution'] == FiniteSet((15, -6, -4))
        
        
        response.reset()
        asyncio.run(solveMode({ "expression": r"""
            \begin{align}
            3 * x^2 & = 2 * y \\
            y &= \frac{3}{2} x \\
            \end{align}
            """, "environment": { } }, response, self.parser))
        
        assert response.hasResult()
        
        assert response.getResult()['result']['solution'] == FiniteSet((0, 0), (1, Rational(3, 2)))
    
    def test_solve_multivariate(self):
        x, y, z = symbols('x y z')
        
        response = TestResponse()
        
        asyncio.run(solveMode({ "expression": r"""
            \begin{cases}
            x + y = z \\
            x - y = -z \\
            \end{cases}
            """,
            "symbols": ["x", "y"],
            "environment": {  } }, response, self.parser))
        
        assert response.hasResult()
        
        assert response.getResult()['result']['solution'] == FiniteSet((0, z))
        assert response.getResult()['result']['symbols'] == [ x, y ]
        
        response.reset()        
        asyncio.run(solveMode({ "expression": r"""
            \begin{cases}
            x + y = z \\
            x - y = -z \\
            \end{cases}
            """,
            "symbols": ["y", "z"],
            "environment": {  } }, response, self.parser))
        
        assert response.hasResult()
        
        assert response.getResult()['result']['solution'] == EmptySet
        assert response.getResult()['result']['symbols'] == [ y, z ]
