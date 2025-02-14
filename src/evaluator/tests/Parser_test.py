from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils

from sympy import *

class TestParse:
    def test_mathematical_constants(self):
        assert ObsimatEnvironmentUtils.parse_latex(r"\pi", {}) == S.Pi
        assert ObsimatEnvironmentUtils.parse_latex(r"e", {}) == S.Exp1
        assert ObsimatEnvironmentUtils.parse_latex(r"i", {}) == I
    
    def test_ambigous_function_expressions(self):
        a, b, c = symbols('a b c')
        assert ObsimatEnvironmentUtils.parse_latex(r"(\sin(a) - b)^2 + c + (\sin(b) - a)", {}) == (sin(a) - b)**2 + c + sin(b) - a
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin(a) - b", {}) == sin(a) - b
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin(5) - 75", {}) == sin(5) - 75
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin(a - b)", {}) == sin(a - b)
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin(a - b) - c", {}) == sin(a - b) - c
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin a \cdot b - c", {}) == sin(a) * b - c
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin{a \cdot b} - c", {}) == sin(a * b) - c
        
    def test_implicit_multiplication(self):
        a, b, c = symbols('a b c')
        assert ObsimatEnvironmentUtils.parse_latex(r"2 a", {}) == 2 * a
        assert ObsimatEnvironmentUtils.parse_latex(r"a b", {}) == a * b
        assert ObsimatEnvironmentUtils.parse_latex(r"a b c", {}) == a * b * c
        assert ObsimatEnvironmentUtils.parse_latex(r"a b \cdot c", {}) == a * b * c
        assert ObsimatEnvironmentUtils.parse_latex(r"a \cdot b c", {}) == a * b * c
        
        # functions 
        assert ObsimatEnvironmentUtils.parse_latex(r"b \sin(a)", {}) == sin(a) * b
        assert ObsimatEnvironmentUtils.parse_latex(r"\sin(a) b", {}) == sin(a) * b
        
        # fractions
        assert ObsimatEnvironmentUtils.parse_latex(r"\frac{a}{b} c", {}) == a / b * c
        assert ObsimatEnvironmentUtils.parse_latex(r"c \frac{a}{b}", {}) == a / b * c
        
        # matricies
        assert ObsimatEnvironmentUtils.parse_latex(r"""
            \begin{bmatrix}
            10 \\
            20
            \end{bmatrix}
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """, {}) == Matrix([[10], [20]]) * Matrix([[30, 40]])
        
        assert ObsimatEnvironmentUtils.parse_latex(r"""
            a
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """, {}) == a * Matrix([[30, 40]])
                
        assert ObsimatEnvironmentUtils.parse_latex(r"""
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            a
            """, {}) == a * Matrix([[30, 40]])
        
        # powers
        assert ObsimatEnvironmentUtils.parse_latex(r"b a^2", {}) == a**2 * b
        assert ObsimatEnvironmentUtils.parse_latex(r"a^2 b", {}) == a**2 * b
        
        #scripts
        x1 = symbols("x_{1}")
        assert ObsimatEnvironmentUtils.parse_latex(r"b x_1", {}) == x1 * b
        assert ObsimatEnvironmentUtils.parse_latex(r"x_1 b", {}) == x1 * b