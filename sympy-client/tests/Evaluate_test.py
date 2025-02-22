from grammar.ObsimatLatexParser import ObsimatLatexParser
from tests.TestResponse import TestResponse
from modes.EvaluateMode import evaluateMode
import asyncio

from sympy import *


## Tests the evaluate mode.
class TestEvaluate:
    parser = ObsimatLatexParser()
    
    def test_simple_evaluate(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": "1+1", "environment": {}}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()
            
        with evaluate(False):
            assert result['result'] == 2
            
    def test_escaped_spaces(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"1\ + \ 1", "environment": {}}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()
            
        with evaluate(False):
            assert result['result'] == 2
        
        
    def test_matrix_single_line(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"2 \cdot \begin{bmatrix} 1 \\ 1 \end{bmatrix}", "environment": {}}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'].rhs == 2 * Matrix([[1], [1]])
        
                
    def test_matrix_multi_line(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"""
        2
        \cdot 
        \begin{bmatrix} 
        1 \\ 1
        \end{bmatrix}
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'].rhs == 2 * Matrix([[1], [1]])
        
    def test_matrix_normal(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"""
        \Vert
        \begin{bmatrix}
        20 \\
        30 \\
        40 \\
        50
        \end{bmatrix}
        \Vert
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'] == sqrt(20**2 + 30**2 + 40**2 + 50**2)
        
    def test_matrix_inner_prodcut(self):
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"""
        \langle 
        \begin{bmatrix}
        1 \\
        2
        \end{bmatrix}
        |
        \begin{bmatrix}
        2 \\
        4
        \end{bmatrix}
        \rangle
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'] == 1 * 2 + 2 * 4
        
        
    def test_relational_evaluation(self):
        a, b = symbols("a b")
        
        response = TestResponse()
        asyncio.run(evaluateMode({"expression": r"""
        5 + 5 + 5 + 5 = 10 + 10
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'] == 20
        
        response.reset()
        asyncio.run(evaluateMode({"expression": r"""
        a = b = (a - b)^2
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'].rhs == (a**2 + b**2 - 2 * a * b)
        
        response.reset()
        asyncio.run(evaluateMode({"expression": r"""
        1 = 2 = 1
        """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()

        assert result['result'] == 1
        
        response.reset()
        asyncio.run(evaluateMode({"expression": r"""
            \begin{cases}
            2 + 2 + 2 + 2 &= 4 + 2 + 2 \\
                          &= 4 + 4
            \end{cases}
            """, "environment": {}}, response, self.parser))
        
        assert response.hasResult()
        
        result = response.getResult()
        
        assert result['result'] == 8
        assert result['metadata']['start_line'] == 4
        assert result['metadata']['end_line'] == 4
    
    def test_variable_substitution(self):
        
        response = TestResponse()
        
        asyncio.run(evaluateMode({
            "expression": r"a + b",
            "environment": {
                "variables": {
                    "a": "2",
                    "b": "3"
                    }
                }
            },
            response,
            self.parser
        ))
        
        assert response.hasResult()
        assert response.getResult()['result'] == 5
        
        response.reset()
        asyncio.run(evaluateMode({
            "expression": r"A^T B",
            "environment": {
                "variables": {
                    "A": r"""
                    \begin{bmatrix}
                    1 \\ 2
                    \end{bmatrix}
                    """,
                    "B": r"""
                    \begin{bmatrix}
                    3 \\ 4
                    \end{bmatrix}
                    """
                    }
                }
            },
            response,
            self.parser
        ))
        
        assert response.hasResult()
        assert response.getResult()['result'].rhs == Matrix([11])
        
        response.reset()
        asyncio.run(evaluateMode({
            "expression": r"\sin{abc}",
            "environment": {
                "variables": {
                    "abc": "1"
                    }
                }
            },
            response,
            self.parser
        ))
        
        assert response.hasResult()
        assert response.getResult()['result'] == sin(1)
        
                
        response.reset()
        asyncio.run(evaluateMode({
            "expression": r"\sqrt{ val_{sub} + val_2^val_{three}}",
            "environment": {
                "variables": {
                    "val_{sub}": "7",
                    "val_2": "3",
                    "val_{three}": "2"
                    }
                }
            },
            response,
            self.parser
        ))
        
        assert response.hasResult()
        assert response.getResult()['result'] == 4
        
        
    def test_gradient(self):
        x, y = symbols("x y")
        response = TestResponse()
        
        asyncio.run(evaluateMode({
            "expression": r"\nabla (x^2 y + y^2 x)",
            "environment": { }
            },
            response,
            self.parser
        ))
        
        assert response.hasResult()
        assert response.getResult()['result'].rhs == Matrix([[y * (2 * x + y), x * (2 * y + x)]])
    
    # TODO: missing unit conversion tests.