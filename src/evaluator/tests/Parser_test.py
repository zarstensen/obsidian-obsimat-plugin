from grammar.ObsimatLatexParser import ObsimatLatexParser
from grammar.SystemOfExpr import SystemOfExpr

from sympy import *

class TestParse:
    
    def test_relations(self):
        parser = ObsimatLatexParser()
        x, y, z = symbols("x y z")
        assert parser.doparse(r"x=y") == Eq(x, y)
        
        result = parser.doparse(r"x = y < z")
    
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 2
        
        assert result.get_all_expr() == (Eq(x, y), Lt(y, z))
        
    
    def test_matrix(self):
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"\begin{bmatrix} 1 \\ 2 \end{bmatrix}") == Matrix([[1], [2]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \end{bmatrix}") == Matrix([[1, 2]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}") == Matrix([[1, 2], [3, 4]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}") == Matrix([[1, 2], [3, 4], [5, 6]])
    
    def test_mathematical_constants(self):
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"\pi") == S.Pi
        assert parser.doparse(r"e") == S.Exp1
        assert parser.doparse(r"i") == I
    
    def test_ambigous_function_expressions(self):
        a, b, c = symbols('a b c')
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"(\sin(a) - b)^2 + c + (\sin(b) - a)") == (sin(a) - b)**2 + c + sin(b) - a
        assert parser.doparse(r"\sin(a) - b") == sin(a) - b
        assert parser.doparse(r"\sin(5) - 75") == sin(5) - 75
        assert parser.doparse(r"\sin(a - b)") == sin(a - b)
        assert parser.doparse(r"\sin(a - b) - c") == sin(a - b) - c
        assert parser.doparse(r"\sin a \cdot b - c") == sin(a) * b - c
        assert parser.doparse(r"\sin{a \cdot b} - c") == sin(a * b) - c
        
    def test_implicit_multiplication(self):
        a, b, c = symbols('a b c')
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"2 a") == 2 * a
        assert parser.doparse(r"a b") == a * b
        assert parser.doparse(r"a b c") == a * b * c
        assert parser.doparse(r"a b \cdot c") == a * b * c
        assert parser.doparse(r"a \cdot b c") == a * b * c
        
        # functions 
        assert parser.doparse(r"b \sin(a)") == sin(a) * b
        assert parser.doparse(r"\sin(a) b") == sin(a) * b
        
        # fractions
        assert parser.doparse(r"\frac{a}{b} c") == a / b * c
        assert parser.doparse(r"c \frac{a}{b}") == a / b * c
        
        # matricies
        assert parser.doparse(r"""
            \begin{bmatrix}
            10 \\
            20
            \end{bmatrix}
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == Matrix([[10], [20]]) * Matrix([[30, 40]])
        
        assert parser.doparse(r"""
            a
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == a * Matrix([[30, 40]])
                
        assert parser.doparse(r"""
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            a
            """) == a * Matrix([[30, 40]])
        
        # powers
        assert parser.doparse(r"b a^2") == a**2 * b
        assert parser.doparse(r"a^2 b") == a**2 * b
        
        #scripts
        x1 = symbols("x_{1}")
        assert parser.doparse(r"b x_1") == x1 * b
        assert parser.doparse(r"x_1 b") == x1 * b
    
    def test_partial_relations(self):
        x, y = symbols("x y")
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"= 25").rhs == 25
        assert parser.doparse(r"x = ").lhs == x
        assert parser.doparse(r"x =& ").lhs == x
        assert parser.doparse(r"&=& 25").rhs == 25
        # check if normal relations have not broken
        assert parser.doparse(r"x & = & y") == Eq(x, y) 
        
    def test_multi_expressions(self):
        x, y, z = symbols("x y z")
        parser = ObsimatLatexParser()
        
        result = parser.doparse(r"""
            \begin{align}
            x & = 2y 5z \\
            y & = x^2 \\
            z & = x + 2\frac{y}{x} \\
            \end{align}
            """)
        
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 3
        
        assert result.get_expr(0) == Eq(x, 2*y * 5 * z)
        assert result.get_location(0).line == 3
        assert result.get_location(0).end_line == 3

        assert result.get_expr(1) == Eq(y, x**2)
        assert result.get_location(1).line == 4
        assert result.get_location(1).end_line == 4

        assert result.get_expr(2) == Eq(z, x + 2 * y / x)
        assert result.get_location(2).line == 5
        assert result.get_location(2).end_line == 5


        result = parser.doparse(r"""
            \begin{cases}
            x
            \end{cases}
            """)
        
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1
        
        assert result.get_expr(0) == x
        assert result.get_location(0).line == 3
        
        result = parser.doparse(r"""
            \begin{cases}
            x & = 2y
            \end{cases}
            """)
        
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1
        
        assert result.get_expr(0) == Eq(x, 2*y)
        assert result.get_location(0).line == 3
        