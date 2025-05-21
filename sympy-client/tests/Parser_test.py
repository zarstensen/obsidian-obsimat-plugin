from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.grammar.SystemOfExpr import SystemOfExpr

from sympy import *

class TestParse:
    parser = ObsimatLatexParser()

    def test_basic(self):
        a, b = symbols('a b')
        result = self.parser.doparse(r'-a + b + \frac{{a}}{b} + {a}^{b} \cdot f(a 25^2 symbol^{yaysymbol}) - \frac{50 - 70}5^{-99} - \frac{{km}}{{h}}')
        assert result == -a + b

    def test_relations(self):
        x, y, z = symbols("x y z")
        assert self.parser.doparse(r"x=y") == Eq(x, y)
        
        result = self.parser.doparse(r"x = y < z")
    
        assert isinstance(result, And)
        assert len(result.args) == 2
        
        assert result.args == (Eq(x, y), Lt(y, z))
        
    
    def test_matrix(self):
        
        assert self.parser.doparse(r"\begin{bmatrix} 1 \\ 2 \end{bmatrix}") == Matrix([[1], [2]])
        assert self.parser.doparse(r"\begin{bmatrix} 1 & 2 \end{bmatrix}") == Matrix([[1, 2]])
        assert self.parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}") == Matrix([[1, 2], [3, 4]])
        assert self.parser.doparse(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}") == Matrix([[1, 2], [3, 4], [5, 6]])
    
    def test_mathematical_constants(self):
        
        assert self.parser.doparse(r"\pi") == S.Pi
        assert self.parser.doparse(r"e") == S.Exp1
        assert self.parser.doparse(r"i") == I
    
    def test_ambigous_function_expressions(self):
        a, b, c = symbols('a b c')
        
        assert self.parser.doparse(r"(\sin(a) - b)^2 + c + (\sin(b) - a)") == (sin(a) - b)**2 + c + sin(b) - a
        assert self.parser.doparse(r"\sin(a) - b") == sin(a) - b
        assert self.parser.doparse(r"\sin(5) - 75") == sin(5) - 75
        assert self.parser.doparse(r"\sin(a - b)") == sin(a - b)
        assert self.parser.doparse(r"\sin(a - b) - c") == sin(a - b) - c
        assert self.parser.doparse(r"\sin a \cdot b - c") == sin(a) * b - c
        assert self.parser.doparse(r"\sin{a \cdot b} - c") == sin(a * b) - c
        
    def test_implicit_multiplication(self):
        a, b, c = symbols('a b c')
        
        assert self.parser.doparse(r"2 a") == 2 * a
        assert self.parser.doparse(r"a b") == a * b
        assert self.parser.doparse(r"a b c") == a * b * c
        assert self.parser.doparse(r"a b \cdot c") == a * b * c
        assert self.parser.doparse(r"a \cdot b c") == a * b * c
        
        # functions 
        assert self.parser.doparse(r"b \sin(a)") == sin(a) * b
        assert self.parser.doparse(r"\sin(a) b") == sin(a) * b
        
        # fractions
        assert self.parser.doparse(r"\frac{a}{b} c") == a / b * c
        assert self.parser.doparse(r"c \frac{a}{b}") == a / b * c
        
        # matricies
        assert self.parser.doparse(r"""
            \begin{bmatrix}
            10 \\
            20
            \end{bmatrix}
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == Matrix([[10], [20]]) * Matrix([[30, 40]])
        
        assert self.parser.doparse(r"""
            a
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == a * Matrix([[30, 40]])
                
        assert self.parser.doparse(r"""
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            a
            """) == a * Matrix([[30, 40]])
        
        # powers
        assert self.parser.doparse(r"b a^2") == a**2 * b
        assert self.parser.doparse(r"a^2 b") == a**2 * b
        
        #scripts
        x1 = symbols("x_1")
        assert self.parser.doparse(r"b x_1") == x1 * b
        assert self.parser.doparse(r"x_1 b") == x1 * b
        
        f, x = symbols("f x")
        
        assert self.parser.doparse("f (x)") == f * x
        assert self.parser.doparse("f(x)") == Function(f)(x)
    
    def test_partial_relations(self):
        x, y = symbols("x y")
        
        assert self.parser.doparse(r"= 25").rhs == 25
        assert self.parser.doparse(r"x = ").lhs == x
        assert self.parser.doparse(r"x =& ").lhs == x
        assert self.parser.doparse(r"&=& 25").rhs == 25
        # check if normal relations have not broken
        assert self.parser.doparse(r"x & = & y") == Eq(x, y) 
        
    def test_multi_expressions(self):
        x, y, z = symbols("x y z")
        
        result = self.parser.doparse(r"""
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


        result = self.parser.doparse(r"""
            \begin{cases}
            x
            \end{cases}
            """)
        
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1
        
        assert result.get_expr(0) == x
        assert result.get_location(0).line == 3
        
        result = self.parser.doparse(r"""
            \begin{cases}
            x & = 2y
            \end{cases}
            """)
        
        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1
        
        assert result.get_expr(0) == Eq(x, 2*y)
        assert result.get_location(0).line == 3
    

    def test_matrix_operations(self):
        result = self.parser.doparse(r"A A^\ast",
        {
            "variables": {
                "A": r"""
\begin{bmatrix}
1 & 2 \\
i & 2 i
\end{bmatrix}    
"""
            }
        })
        
        assert result.doit() == Matrix([[5, - 5 * I], [5 * I, 5]])	
        
    def test_symbols(self):
        s_a = Symbol("variable")
        s_b = Symbol("v")
        s_c = Symbol("a_1")
        s_d = Symbol(r"\mathrm{X}")
        s_e = Symbol(r"\pmb{M}_{some label i;j}")
        s_f = Symbol(r"\alpha_{very_{indexed_{variable}}}")
        
        result = self.parser.doparse(r"variable + v \cdot a_1 + \sqrt{\pmb{M}_{some label i;j}^{\alpha_{very_{indexed_{variable}}}}} + \mathrm{X}^{-1}")
        
        assert result == s_a + s_b * s_c + sqrt(s_e**s_f) + s_d**-1

    def test_symbol_definitions(self):
        result = self.parser.doparse(r"x", { "symbols": { "x": [ "real" ] } })
        assert result == symbols("x", real=True)
        
        x = symbols("x", real=True)
        y = symbols("y", positive=True)
        result = self.parser.doparse(r"a + b", {
            "symbols": {
                "x": [ "real" ], "y": ["positive"]
                },
            "variables": {
                "a": "x + y",
                "b": "y"
            }
            })
        
        assert result == x + y + y
    
    def test_brace_units(self):
        import sympy.physics.units as u
        x, a, b = symbols('x a b')
        result = self.parser.doparse(r"{km} + \sin{x} + \frac{a}{{J}} + b")
        
        assert result == u.km + sin(x) + a / u.joule + b
    
    def test_hessian(self):
        result = self.parser.doparse(r"\mathbf{H}(x^2 + y^2)")
        
        assert result.doit() == Matrix([[2, 0], [0, 2]])
        
    def test_jacobian(self):
        result = self.parser.doparse(r"\mathbf{J}(\begin{bmatrix} x + y \\ x \\ y\end{bmatrix})")
        
        assert result.doit() == Matrix([[1, 1], [1, 0], [0, 1]])
        
    def test_rref(self):
        result = self.parser.doparse(r"\mathrm{rref}(\begin{bmatrix} 20 & 50 \\ 10 & 25\end{bmatrix})")
        
        assert result == Matrix([[1, Rational(5, 2)], [0, 0]])