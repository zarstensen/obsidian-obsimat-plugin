from sympy import *
from sympy.logic.boolalg import *
from sympy_client import LmatEnvironment
from sympy_client.grammar.LatexMatrix import LatexMatrix
from sympy_client.grammar.LatexParser import LatexParser
from sympy.logic.boolalg import *
from sympy_client.grammar.LmatEnvDefStore import LmatEnvDefStore
from sympy_client.grammar.SystemOfExpr import SystemOfExpr


class TestParse:
    parser = LatexParser()

    def _parse_expr(self, expr, environment: LmatEnvironment = {}) -> Expr:
        return self.parser.parse(expr, LmatEnvDefStore(self.parser, environment))

    def test_basic(self):
        a, b, c = symbols('a b c')
        # result = self.parser.doparse(r'-a i + b \pi + e + \frac{{a}}{b} + {a}^{b} \cdot f(a 25^2 symbol^{yaysymbol}) - \frac{50 - 70}5^{-99} - \frac{{km}}{{h}} \over \sin x + \sqrt[5]{x}')
        result = self._parse_expr(r'-a i \cdot (5 + 7)^c + b')
        assert result == -a * I * (5 + 7) ** c + b

    def test_non_base_10_numbers(self):
        result = self._parse_expr(r"0b1001 - \mathrm{0b0001} + 0\mathrm{b}1000")
        assert result == 16

        result = self._parse_expr(r"\frac{\mathrm{0XFF}}{0xf} + 0123")
        assert result == 140

    def test_trig_funcs(self):
        x, y, abc = symbols('x y abc')
        assert self._parse_expr(r'\sin x') == sin(x)
        assert self._parse_expr(r'\sin^y x') == sin(x)**y
        assert simplify(self._parse_expr(r'\frac{\sin(abc)}{\cos {abc}}')) == tan(abc)
        assert self._parse_expr(r'\arctan{abc}') == atan(abc)
        assert self._parse_expr(r'\mathrm{arcosh} y') == acosh(y)
        assert self._parse_expr(r'\operatorname{arcosh} y') == acosh(y)
        assert self._parse_expr(r'\mathrm{sech} y') == sech(y)
        assert self._parse_expr(r'\mathrm{arsech} y') == asech(y)
        assert self._parse_expr(r'\mathrm{csch} y') == csch(y)
        assert self._parse_expr(r'\mathrm{arcsch} y') == acsch(y)
        assert self._parse_expr(r'\coth y') == coth(y)
        assert self._parse_expr(r'\mathrm{arcoth} y') == acoth(y)


    def test_relations(self):
        x, y, z = symbols("x y z")
        assert self._parse_expr(r"x=y") == Eq(x, y)

        result = self._parse_expr(r"x = y < z")

        assert isinstance(result, SystemOfExpr)
        assert len(result) == 2

        assert result.get_all_expr() == (Eq(x, y), Lt(y, z))


    def test_matrix(self):

        assert self._parse_expr(r"\begin{bmatrix} 1 \\ 2 \end{bmatrix}") == Matrix([[1], [2]])
        assert self._parse_expr(r"\begin{bmatrix} 1 & 2 \end{bmatrix}") == Matrix([[1, 2]])
        assert self._parse_expr(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix}") == Matrix([[1, 2], [3, 4]])
        assert self._parse_expr(r"\begin{bmatrix} 1 & 2 \\ 3 & 4 \\ 5 & 6 \end{bmatrix}") == Matrix([[1, 2], [3, 4], [5, 6]])

    def test_mathematical_constants(self):

        assert self._parse_expr(r"\pi") == S.Pi
        assert self._parse_expr(r"e") == S.Exp1
        assert self._parse_expr(r"i") == I

    def test_ambigous_function_expressions(self):
        a, b, c = symbols('a b c')

        assert self._parse_expr(r"(\sin(a) - b)^2 + c + (\sin(b) - a)") == (sin(a) - b)**2 + c + sin(b) - a
        assert self._parse_expr(r"\sin(a) - b") == sin(a) - b
        assert self._parse_expr(r"\sin(5) - 75") == sin(5) - 75
        assert self._parse_expr(r"\sin(a - b)") == sin(a - b)
        assert self._parse_expr(r"\sin(a - b) - c") == sin(a - b) - c
        assert self._parse_expr(r"\sin a \cdot b - c") == sin(a) * b - c
        assert self._parse_expr(r"\sin{a \cdot b} - c") == sin(a * b) - c

    def test_implicit_multiplication(self):
        a, b, c = symbols('a b c')

        assert self._parse_expr(r"2 a") == 2 * a
        assert self._parse_expr(r"a b") == a * b
        assert self._parse_expr(r"a b c") == a * b * c
        assert self._parse_expr(r"a b \cdot c") == a * b * c
        assert self._parse_expr(r"a \cdot b c") == a * b * c

        # indexed_symbols
        x1, x2 = symbols('x_{1} x_{2}')

        assert self._parse_expr(r"x_{1} x_{2}") == x1 * x2

        # functions
        assert self._parse_expr(r"b \sin(a)") == sin(a) * b
        assert self._parse_expr(r"\sin(a) b") == sin(a) * b

        # fractions
        assert self._parse_expr(r"\frac{a}{b} c") == a / b * c
        assert self._parse_expr(r"c \frac{a}{b}") == a / b * c

        # matricies
        assert self._parse_expr(r"""
            \begin{bmatrix}
            10 \\
            20
            \end{bmatrix}
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == Matrix([[10], [20]]) * Matrix([[30, 40]])

        assert self._parse_expr(r"""
            a
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            """) == a * Matrix([[30, 40]])

        assert self._parse_expr(r"""
            \begin{bmatrix}
            30 &
            40
            \end{bmatrix}
            a
            """) == a * Matrix([[30, 40]])

        # powers
        assert self._parse_expr(r"b a^2") == a**2 * b
        assert self._parse_expr(r"a^2 b") == a**2 * b

        #scripts
        x1 = symbols("x_{1}")
        assert self._parse_expr(r"b x_1") == x1 * b
        assert self._parse_expr(r"x_1 b") == x1 * b

        f, x = symbols("f x")

        assert self._parse_expr("f (x)") == f * x
        assert self._parse_expr("f(x)") == Function('f')(x)

    def test_partial_relations(self):
        x, y = symbols("x y")

        assert self._parse_expr(r"= 25").rhs == 25
        assert self._parse_expr(r"x = ").lhs == x
        assert self._parse_expr(r"x =& ").lhs == x
        assert self._parse_expr(r"&=& 25").rhs == 25
        # check if normal relations have not broken
        assert self._parse_expr(r"x & = & y") == Eq(x, y)

    def test_multi_expressions(self):
        x, y, z = symbols("x y z")

        result = self._parse_expr(r"""
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
        assert result.get_location(2).end_line == None


        result = self._parse_expr(r"""
            \begin{cases}
            x
            \end{cases}
            """)

        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1

        assert result.get_expr(0) == x
        assert result.get_location(0).line == 3

        result = self._parse_expr(r"""
            \begin{cases}
            x & = 2y
            \end{cases}
            """)

        assert isinstance(result, SystemOfExpr)
        assert len(result) == 1

        assert result.get_expr(0) == Eq(x, 2*y)
        assert result.get_location(0).line == 3


    def test_matrix_operations(self):
        result = self._parse_expr(r"A A^\ast",
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
        s_c = Symbol("a_{1}")
        s_d = Symbol(r"\mathrm{X}")
        s_e = Symbol(r"\pmb{M}_{some label i;j}")
        s_f = Symbol(r"\alpha_{very_{indexed_{variable}}}")

        result = self._parse_expr(r"variable + v \cdot a_1 + \sqrt{\pmb{M}_{some label i;j}^{\alpha_{very_{indexed_{variable}}}}} + \mathrm{X}^{-1}")

        assert result == s_a + s_b * s_c + sqrt(s_e**s_f) + s_d**-1

    def test_symbol_definitions(self):
        result = self._parse_expr(r"x", { "symbols": { "x": [ "real" ] } })
        assert result == symbols("x", real=True)

        x = symbols("x", real=True)
        y = symbols("y", positive=True)
        result = self._parse_expr(r"a + b", {
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

        assert self._parse_expr(r"{a + b}^2 + {s}^2") == u.second**2 + (a + b)**2

        result = self._parse_expr(r"{km} + \sin{x} + \frac{a}{{J}} + b")
        assert result == u.km + sin(x) + a / u.joule + b

    def test_hessian(self):
        result = self._parse_expr(r"\mathbf{H}(x^2 + y^2)")

        assert result.doit() == Matrix([[2, 0], [0, 2]])

    def test_jacobian(self):
        result = self._parse_expr(r"\mathbf{J}(\begin{bmatrix} x + y \\ x \\ y\end{bmatrix})")

        assert result.doit() == Matrix([[1, 1], [1, 0], [0, 1]])

    def test_rref(self):
        result = self._parse_expr(r"\mathrm{rref}(\begin{bmatrix} 20 & 50 \\ 10 & 25\end{bmatrix})")

        assert result == Matrix([[1, Rational(5, 2)], [0, 0]])

    def test_percent_permille(self):
        result = self._parse_expr(r"25\% - 5\textperthousand")

        assert abs(result - (0.25 - 0.005)) <= 1e-14

    def test_propositions(self):
        a, b, c, d, e, f, g, h, i = symbols('A B C D E F G H I')

        # test presedence
        result = self._parse_expr(r"\neg A \odot B \oplus C \bar \vee D \wedge E \overline \wedge F \vee G \implies H \iff I")
        assert simplify(result) == simplify(Equivalent(Implies(Or(Nand(And(Nor(Xor(Xnor(Not(a), b), c), d), e), f), g), h), i))

        result = self._parse_expr(r"A \iff B \Longleftrightarrow C \longleftrightarrow D \leftrightharpoons E \rightleftharpoons F ")
        assert simplify(result) == simplify(Equivalent(a, b, c, d, e, f))

        result = self._parse_expr(r"A \implies B \to C \Longrightarrow D \longrightarrow E \Rightarrow F \rightarrow G")
        assert simplify(result) == simplify(a >> (b >> (c >> (d >> (e >> (f >> g))))))

        result = self._parse_expr(r"A \Longleftarrow B \longleftarrow C \Leftarrow D \leftarrow E")
        assert simplify(result) == simplify(a << (b << (c << (d << e))))

        result = self._parse_expr(r"A \vee B")
        assert simplify(result) == simplify(Or(a, b))

        result = self._parse_expr(r"A \bar \wedge B \overline \wedge C")
        assert simplify(result) == simplify(Nand(a, b, c))

        result = self._parse_expr(r"A \wedge B")
        assert simplify(result) == simplify(And(a, b))

        result = self._parse_expr(r"A \bar \vee B \overline \vee C")
        assert simplify(result) == simplify(Nor(a, b, c))

        result = self._parse_expr(r"A \oplus B")
        assert simplify(result) == simplify(Xor(a, b))

        result = self._parse_expr(r"A \odot B")
        assert simplify(result) == simplify(Xnor(a, b))

        result = self._parse_expr(r"\neg A")
        assert simplify(result) == simplify(Not(a))

        result = self._parse_expr(r"\mathrm{T} \implies \mathrm{F}")
        assert simplify(result) == simplify(S.true >> S.false)

    def test_regression_101(self):
        x, y = symbols('x y')

        result = self._parse_expr(r"\sin x^2")

        assert result == sin(x**2)

        result = self._parse_expr(r"\sin(x)^2")

        assert result == sin(x)**2

        result = self._parse_expr(r"\log_{10} x^2")
        assert result == log(x**2, 10)

        result = self._parse_expr(r"\cos |x|")
        assert result == cos(abs(x))

        result = self._parse_expr(r"\sin x \mod y")
        assert result == Mod(sin(x), y)

        result = self._parse_expr(r"\log(x)!")
        assert result == factorial(log(x))

        result = self._parse_expr(r"\log x!!!")
        assert result == log(factorial(factorial(factorial(x))))

    def test_matrix_bracket_persistance(self):
        result = self._parse_expr(r"\begin{pmatrix} 1 & 2 \\ 3 & 4 \end{pmatrix}")

        assert isinstance(result, LatexMatrix)
        assert result.env_begin == r'\begin{pmatrix}'
        assert result.env_end == r'\end{pmatrix}'

        result = self._parse_expr(r"\left\{ \begin{array}{r | c : l} x & y^2 \\ z_3 & \mathrm{uv} \end{array} \right]")

        assert isinstance(result, LatexMatrix)
        assert result.env_begin == r'\left\{ \begin{array}{r | c : l}'
        assert result.env_end == r'\end{array} \right]'
