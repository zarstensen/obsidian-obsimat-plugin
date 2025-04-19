from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.command_handlers.EvalHandler import *
from sympy_client.command_handlers.EvalfHandler import *
from sympy_client.command_handlers.ExpandHandler import *
from sympy_client.command_handlers.FactorHandler import *
from sympy_client.command_handlers.ApartHandler import *

from sympy import *

## Tests the evaluate mode.
class TestEvaluate:
    parser = ObsimatLatexParser()
    
    def test_simple_evaluate(self):
        handler = EvalHandler(self.parser)
        
        result = handler.handle({"expression": "1+1", "environment": {}})
        
        assert result.sympy_expr == 2
            
    def test_escaped_spaces(self):
        handler = EvalHandler(self.parser)
        
        result = handler.handle({"expression": r"1\ + \ 1", "environment": {}})

        assert result.sympy_expr == 2
        
        
    def test_matrix_single_line(self):
        handler = EvalHandler(self.parser)
        
        result = handler.handle({"expression": r"2 \cdot \begin{bmatrix} 1 \\ 1 \end{bmatrix}", "environment": {}})

        assert result.sympy_expr.rhs == 2 * Matrix([[1], [1]])
        
                
    def test_matrix_multi_line(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"""
        2
        \cdot 
        \begin{bmatrix} 
        1 \\ 1
        \end{bmatrix}
        """, "environment": {}})
        
        assert result.sympy_expr.rhs == 2 * Matrix([[1], [1]])
        
    def test_matrix_normal(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"""
        \Vert
        \begin{bmatrix}
        20 \\
        30 \\
        40 \\
        50
        \end{bmatrix}
        \Vert
        """, "environment": {}})

        assert result.sympy_expr == sqrt(20**2 + 30**2 + 40**2 + 50**2)
        
    def test_matrix_inner_prodcut(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"""
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
        """, "environment": {}})

        assert result.sympy_expr == 1 * 2 + 2 * 4
        
        
    def test_relational_evaluation(self):
        a, b = symbols("a b")
        
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"""
        5 + 5 + 5 + 5 = 10 + 10
        """, "environment": {}})

        assert result.sympy_expr == 20
        
        result = handler.handle({"expression": r"""
        a = b = (a - b)^2
        """, "environment": {}})
        
        assert result.sympy_expr == (a - b)**2
        
        result = handler.handle({"expression": r"""
        1 = 2 = 1
        """, "environment": {}})
        
        assert result.sympy_expr == 1
        
        result = handler.handle({"expression": r"""
            \begin{cases}
            2 + 2 + 2 + 2 &= 4 + 2 + 2 \\
                          &= 4 + 4
            \end{cases}
            """, "environment": {}})
        
        assert result.sympy_expr == 8
        assert result.expr_lines == (4, 4)
        
        result = handler.handle({"expression": r"""
            1 = 2 = 3 = 4 = 5 = 6 = 7 = 8 = 9
            """, "environment": {}})

        assert result.sympy_expr == 9
        
    
    def test_variable_substitution(self):
        handler = EvalHandler(self.parser)

        result = handler.handle({
            "expression": r"a + b",
            "environment": {
                "variables": {
                    "a": "2",
                    "b": "3"
                }
            }
        })
        assert result.sympy_expr == 5

        result = handler.handle({
            "expression": r"\alpha",
            "environment": {
                "variables": {
                    "\\alpha": "2"
                }
            }
        })
        assert result.sympy_expr == 2

        result = handler.handle({
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
        })
        assert result.sympy_expr.rhs == Matrix([11])

        result = handler.handle({
            "expression": r"\sin{abc}",
            "environment": {
                "variables": {
                    "abc": "1"
                }
            }
        })
        assert result.sympy_expr == sin(1)

        result = handler.handle({
            "expression": r"\sqrt{ val_{sub} + val_2^val_{three}}",
            "environment": {
                "variables": {
                    "val_{sub}": "7",
                    "val_2": "3",
                    "val_{three}": "2"
                }
            }
        })
        assert result.sympy_expr == 4
        
        
    def test_gradient(self):
        handler = EvalHandler(self.parser)
        
        result = handler.handle({
            "expression": r"\nabla (x^2 y + y^2 x)",
            "environment": {}
        })
        
        x, y = symbols("x y")
        assert result.sympy_expr.rhs == Matrix([[y * (2 * x + y), x * (2 * y + x)]])
    
    def test_evalf(self):
        handler = EvalfHandler(self.parser)
        result = handler.handle({"expression": "5/2", "environment": {}})
        assert result.sympy_expr.rhs == 2.5

    def test_expand(self):
        handler = ExpandHandler(self.parser)
        result = handler.handle({"expression": "(a + b)^2", "environment": {}})
        a, b = symbols("a b")
        assert result.sympy_expr.rhs == a**2 + 2 * a * b + b**2

    def test_factor(self):
        handler = FactorHandler(self.parser)
        result = handler.handle({"expression": "x^3 - 10x^2 + 3x + 54", "environment": {}})
        x = symbols("x")
        assert result.sympy_expr.rhs == (x - 9) * (x - 3) * (x + 2)

    def test_apart(self):
        handler = ApartHandler(self.parser)
        result = handler.handle({"expression": r"\frac{8x + 7}{x^2 + x - 2}", "environment": {}})
        x = symbols("x")
        assert result.sympy_expr.rhs == 3 / (x + 2) + 5 / (x - 1)

    def test_quick_derivative(self):
        handler = ExpandHandler(self.parser)
        result = handler.handle({"expression": "(x^5 + 3x^4 + 2x + 5)'''", "environment": {}})
        x = symbols("x")
        assert result.sympy_expr.rhs == 60 * x**2 + 72 * x

    def test_function(self):
        handler = EvalHandler(self.parser)

        # Standard function
        result = handler.handle({
            "expression": "f(25, -2)",
            "environment": {
                "functions": {
                    "f": {
                        "args": ["x", "y"],
                        "expr": "2x + y^2"
                    }
                }
            }
        })
        assert result.sympy_expr == 54

        # Function with arg name defined as variables
        result = handler.handle({
            "expression": "f(y)",
            "environment": {
                "functions": {
                    "f": {
                        "args": ["x"],
                        "expr": "2x"
                    }
                },
                "variables": {
                    "x": "-1",
                    "y": "99"
                }
            }
        })
        assert result.sympy_expr == 198

        # Function with matrices as input
        result = handler.handle({
            "expression": r"f(\begin{bmatrix} 5 & 10 \end{bmatrix})",
            "environment": {
                "functions": {
                    "f": {
                        "args": ["x"],
                        "expr": "x x^T"
                    }
                }
            }
        })
        assert result.sympy_expr.rhs == Matrix([[125]])
    
    def test_hessian(self):
        handler = EvalHandler(self.parser)
        x, y = symbols('x y')

        # Standard function
        result = handler.handle({
            "expression": r"\mathbf{H}(y x^5 + \sin(y))",
            "environment": {}
        })
        assert result.sympy_expr.rhs == Matrix([
                                                [20 * x**3 * y,     5 * x ** 4],
                                                [5 * x ** 4,        - sin(y)]
                                                ])

        result = handler.handle({
            "expression": r"\mathbf{H}(f)",
            "environment": {
                "functions": {
                    "f": {
                        "args": ["x", "y", "z"],
                        "expr": r"\log(x) + e^y"
                    }
                }
            }
        })
        
        assert result.sympy_expr.rhs == Matrix([
            [- 1 / x**2,    0,      0],
            [0,             E**y,   0],
            [0,             0,      0]
        ])

    
    def test_jacobi(self):
        handler = EvalHandler(self.parser)
        x, y = symbols('x y')

        # Standard function
        result = handler.handle({
            "expression": r"\mathbf{J}(\begin{bmatrix} x^2 \\ y \\ x * y \end{bmatrix})",
            "environment": {}
        })
        assert result.sympy_expr.rhs == Matrix([
            [2 * x, 0],
            [0,     1],
            [y,     x]
        ])

        result = handler.handle({
            "expression": r"\mathbf{J}(f)",
            "environment": {
                "functions": {
                    "f": {
                        "args": ["x", "y", "z"],
                        "expr": r"\begin{bmatrix}\log(x)\\ \sin(y) \\ \cos(x) * \sin(y) \end{bmatrix}"
                    }
                }
            }
        })
        
        assert result.sympy_expr.rhs == Matrix([
            [1 / x,             0,              0],
            [0,                 cos(y),         0],
            [-sin(x) * sin(y),  cos(x) * cos(y),0]
        ])
    
    # TODO: add gradient test (it is already implicitly tested in test_jacobi so not high priority)