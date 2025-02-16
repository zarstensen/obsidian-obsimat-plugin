from grammar.ObsimatLatexParser import ObsimatLatexParser

from sympy import *

class TestParse:
    
    def test_relations(self):
        parser = ObsimatLatexParser()
        x, y, z = symbols("x y z")
        assert parser.doparse(r"x = 2y").sympy_expr() == Eq(x, 2*y)
        assert parser.doparse(r"x = y < z").sympy_expr() == [ Eq(x, y), Lt(y, z) ]
    
    def test_matrix(self):
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"\begin{bmatrix} 1 \\ 2 \end{bmatrix}").sympy_expr() == Matrix([[1], [2]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \end{bmatrix}").sympy_expr() == Matrix([[1, 2]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}").sympy_expr() == Matrix([[1, 2], [3, 4]])
        assert parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}").sympy_expr() == Matrix([[1, 2], [3, 4], [5, 6]])
    
    def test_mathematical_constants(self):
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"\pi").sympy_expr() == S.Pi
        assert parser.doparse(r"e").sympy_expr() == S.Exp1
        assert parser.doparse(r"i").sympy_expr() == I
    
    def test_ambigous_function_expressions(self):
        a, b, c = symbols('a b c')
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"(\sin(a) - b)^2 + c + (\sin(b) - a)").sympy_expr() == (sin(a) - b)**2 + c + sin(b) - a
        assert parser.doparse(r"\sin(a) - b").sympy_expr() == sin(a) - b
        assert parser.doparse(r"\sin(5) - 75").sympy_expr() == sin(5) - 75
        assert parser.doparse(r"\sin(a - b)").sympy_expr() == sin(a - b)
        assert parser.doparse(r"\sin(a - b) - c").sympy_expr() == sin(a - b) - c
        assert parser.doparse(r"\sin a \cdot b - c").sympy_expr() == sin(a) * b - c
        assert parser.doparse(r"\sin{a \cdot b} - c").sympy_expr() == sin(a * b) - c
        
    def test_implicit_multiplication(self):
        a, b, c = symbols('a b c')
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"2 a").sympy_expr() == 2 * a
        assert parser.doparse(r"a b").sympy_expr() == a * b
        assert parser.doparse(r"a b c").sympy_expr() == a * b * c
        assert parser.doparse(r"a b \cdot c").sympy_expr() == a * b * c
        assert parser.doparse(r"a \cdot b c").sympy_expr() == a * b * c
        
        # functions 
        assert parser.doparse(r"b \sin(a)").sympy_expr() == sin(a) * b
        assert parser.doparse(r"\sin(a) b").sympy_expr() == sin(a) * b
        
        # fractions
        assert parser.doparse(r"\frac{a}{b} c").sympy_expr() == a / b * c
        assert parser.doparse(r"c \frac{a}{b}").sympy_expr() == a / b * c
        
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
            """).sympy_expr() == Matrix([[10], [20]]) * Matrix([[30, 40]])
        
        assert parser.doparse(r"""
            a
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """).sympy_expr() == a * Matrix([[30, 40]])
                
        assert parser.doparse(r"""
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            a
            """).sympy_expr() == a * Matrix([[30, 40]])
        
        # powers
        assert parser.doparse(r"b a^2").sympy_expr() == a**2 * b
        assert parser.doparse(r"a^2 b").sympy_expr() == a**2 * b
        
        #scripts
        x1 = symbols("x_{1}")
        assert parser.doparse(r"b x_1").sympy_expr() == x1 * b
        assert parser.doparse(r"x_1 b").sympy_expr() == x1 * b
    
    def test_partial_relations(self):
        x, y = symbols("x y")
        parser = ObsimatLatexParser()
        
        assert parser.doparse(r"= 25").sympy_expr().rhs == 25
        assert parser.doparse(r"x = ").sympy_expr().lhs == x
        assert parser.doparse(r"x =& ").sympy_expr().lhs == x
        assert parser.doparse(r"&=& 25").sympy_expr().rhs == 25
        # check if normal relations have not broken
        assert parser.doparse(r"x & = & y").sympy_expr() == Eq(x, y) 
        
    def test_multi_expressions(self):
        x, y, z = symbols("x y z")
        parser = ObsimatLatexParser()
        
        result = parser.doparse(r"""
            \begin{align}
            x & = 2y 5z \\
            y & = x^2 \\
            z & = x + 2\frac{y}{x} \\
            \end{align}
            """).sympy_expr()
        
        assert len(result) == 3
        
        assert result[0].sympy_expr() == Eq(x, 2*y * 5 * z)
        assert result[0].location().line == 3
        assert result[0].location().end_line == 3

        assert result[1].sympy_expr() == Eq(y, x**2)
        assert result[1].location().line == 4
        assert result[1].location().end_line == 4

        assert result[2].sympy_expr() == Eq(z, x + 2 * y / x)
        assert result[2].location().line == 5
        assert result[2].location().end_line == 5


        result = parser.doparse(r"""
            \begin{cases}
            x
            \end{cases}
            """).sympy_expr()
        
        assert len(result) == 1
        
        assert result[0].sympy_expr() == x
        assert result[0].location().line == 3
        
        result = parser.doparse(r"""
            \begin{cases}
            x & = 2y
            \end{cases}
            """).sympy_expr()
        
        assert len(result) == 1
        
        assert result[0].sympy_expr() == Eq(x, 2*y)
        assert result[0].location().line == 3
        