from sympy.testing.pytest import XFAIL
from sympy.external import import_module

from sympy.concrete.products import Product
from sympy.concrete.summations import Sum
from sympy.core.function import Derivative, Function
from sympy.core.numbers import E, oo, Rational
from sympy.core.power import Pow
from sympy.core.parameters import evaluate
from sympy.core.relational import GreaterThan, LessThan, StrictGreaterThan, StrictLessThan, Unequality
from sympy.core.symbol import Symbol
from sympy.functions.combinatorial.factorials import binomial, factorial
from sympy.functions.elementary.complexes import Abs, conjugate
from sympy.functions.elementary.exponential import exp, log
from sympy.functions.elementary.integers import ceiling, floor
from sympy.functions.elementary.miscellaneous import root, sqrt, Min, Max
from sympy.functions.elementary.trigonometric import asin, cos, csc, sec, sin, tan
from sympy.integrals.integrals import Integral
from sympy.series.limits import Limit
from sympy import Expr, Matrix, MatAdd, MatMul, Transpose, Trace
from sympy import I, simplify, expand

from sympy.core.relational import Eq, Ne, Lt, Le, Gt, Ge
from sympy.physics.quantum import Bra, Ket, InnerProduct
from sympy.abc import x, y, z, a, b, c, d, t, k, n

from .test_latex import theta, f, _Add, _Mul, _Pow, _Sqrt, _Conjugate, _Abs, _factorial, _exp, _binomial

from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser

xy = Symbol('xy')

lark = import_module("lark")

# disable tests if lark is not present
disabled = lark is None

# shorthand definitions that are only needed for the Lark LaTeX parser
def _Min(*args):
    return Min(*args, evaluate=False)


def _Max(*args):
    return Max(*args, evaluate=False)


def _log(a, b=E):
    if b == E:
        return log(a, evaluate=False)
    else:
        return log(a, b, evaluate=False)


def _MatAdd(a, b):
    return MatAdd(a, b, evaluate=False)


def _MatMul(a, b):
    return MatMul(a, b, evaluate=False)

latex_parser = ObsimatLatexParser()
def parse_latex_lark(latex_str):
    return latex_parser.doparse(latex_str, {})

# These LaTeX strings should parse to the corresponding SymPy expression
SYMBOL_EXPRESSION_PAIRS = [
    (r"x_0", Symbol('x_{0}')),
    (r"x_{1}", Symbol('x_{1}')),
    (r"x_a", Symbol('x_{a}')),
    (r"x_{b}", Symbol('x_{b}')),
    (r"h_\theta", Symbol('h_{\\theta}')),
    (r"h_{\theta}", Symbol('h_{\\theta}')),
    (r"y''_1", Symbol("y''_{1}")),
    (r"y_1''", Symbol("y_{1}''")),
    (r"\mathit{x}", Symbol('\\mathit{x}')),
    (r"\mathbf{test}", Symbol('\\mathbf{test}')),
    (r"\mathit{TEST}", Symbol('\\mathit{TEST}')),
    (r"\mathit{HELLO world}", Symbol('\\mathit{HELLO world}')),
    (r"a'", Symbol("a'")),
    (r"a''", Symbol("a''")),
    (r"\alpha'", Symbol("\\alpha'")),
    (r"\alpha''", Symbol("\\alpha''")),
    (r"a_b", Symbol("a_{b}")),
    (r"a_b'", Symbol("a_{b}'")),
    (r"a'_b", Symbol("a'_{b}")),
    (r"a'_b'", Symbol("a'_{b}'")),
    (r"a_{b'}", Symbol("a_{b'}")),
    (r"a_{b'}'", Symbol("a_{b'}'")),
    (r"a'_{b'}", Symbol("a'_{b'}")),
    (r"a'_{b'}'", Symbol("a'_{b'}'")),
    (r"\mathit{foo}'", Symbol("\\mathit{foo}'")),
    (r"\mathrm{foo'}", Symbol("\\mathrm{foo'}")),
    (r"\pmb{foo'}'", Symbol("\\pmb{foo'}'")),
    (r"a_b''", Symbol("a_{b}''")),
    (r"a''_b", Symbol("a''_{b}")),
    (r"a''_b'''", Symbol("a''_{b}'''")),
    (r"a_{b''}", Symbol("a_{b''}")),
    (r"a_{b''}''", Symbol("a_{b''}''")),
    (r"a''_{b''}", Symbol("a''_{b''}")),
    (r"a''_{b''}'''", Symbol("a''_{b''}'''")),
    (r"\mathit{foo}''", Symbol("\\mathit{foo}''")),
    (r"\mathit{foo''}", Symbol("\\mathit{foo''}")),
    (r"\mathit{foo''}'''", Symbol("\\mathit{foo''}'''")),
    (r"a_\alpha", Symbol("a_{\\alpha}")),
    (r"a_\alpha'", Symbol("a_{\\alpha}'")),
    (r"a'_\alpha", Symbol("a'_{\\alpha}")),
    (r"a'_\alpha'", Symbol("a'_{\\alpha}'")),
    (r"a_{\alpha'}", Symbol("a_{\\alpha'}")),
    (r"a_{\alpha'}'", Symbol("a_{\\alpha'}'")),
    (r"a'_{\alpha'}", Symbol("a'_{\\alpha'}")),
    (r"a'_{\alpha'}'", Symbol("a'_{\\alpha'}'")),
    (r"a_\alpha''", Symbol("a_{\\alpha}''")),
    (r"a''_\alpha", Symbol("a''_{\\alpha}")),
    (r"a''_\alpha'''", Symbol("a''_{\\alpha}'''")),
    (r"a_{\alpha''}", Symbol("a_{\\alpha''}")),
    (r"a_{\alpha''}''", Symbol("a_{\\alpha''}''")),
    (r"a''_{\alpha''}", Symbol("a''_{\\alpha''}")),
    (r"a''_{\alpha''}'''", Symbol("a''_{\\alpha''}'''")),
    (r"\alpha_b", Symbol("\\alpha_{b}")),
    (r"\alpha_b'", Symbol("\\alpha_{b}'")),
    (r"\alpha'_b", Symbol("\\alpha'_{b}")),
    (r"\alpha'_b'", Symbol("\\alpha'_{b}'")),
    (r"\alpha_{b'}", Symbol("\\alpha_{b'}")),
    (r"\alpha_{b'}'", Symbol("\\alpha_{b'}'")),
    (r"\alpha'_{b'}", Symbol("\\alpha'_{b'}")),
    (r"\alpha'_{b'}'", Symbol("\\alpha'_{b'}'")),
    (r"\alpha_b''", Symbol("\\alpha_{b}''")),
    (r"\alpha''_b", Symbol("\\alpha''_{b}")),
    (r"\alpha''_b'''", Symbol("\\alpha''_{b}'''")),
    (r"\alpha_{b''}", Symbol("\\alpha_{b''}")),
    (r"\alpha_{b''}''", Symbol("\\alpha_{b''}''")),
    (r"\alpha''_{b''}", Symbol("\\alpha''_{b''}")),
    (r"\alpha''_{b''}'''", Symbol("\\alpha''_{b''}'''")),
    (r"\alpha_\beta", Symbol("\\alpha_{\\beta}")),
    (r"\alpha_{\beta}", Symbol("\\alpha_{\\beta}")),
    (r"\alpha_{\beta'}", Symbol("\\alpha_{\\beta'}")),
    (r"\alpha_{\beta''}", Symbol("\\alpha_{\\beta''}")),
    (r"\alpha'_\beta", Symbol("\\alpha'_{\\beta}")),
    (r"\alpha'_{\beta}", Symbol("\\alpha'_{\\beta}")),
    (r"\alpha'_{\beta'}", Symbol("\\alpha'_{\\beta'}")),
    (r"\alpha'_{\beta''}", Symbol("\\alpha'_{\\beta''}")),
    (r"\alpha''_\beta", Symbol("\\alpha''_{\\beta}")),
    (r"\alpha''_{\beta}", Symbol("\\alpha''_{\\beta}")),
    (r"\alpha''_{\beta'}", Symbol("\\alpha''_{\\beta'}")),
    (r"\alpha''_{\beta''}", Symbol("\\alpha''_{\\beta''}")),
    (r"\alpha_\beta'", Symbol("\\alpha_{\\beta}'")),
    (r"\alpha_{\beta}'", Symbol("\\alpha_{\\beta}'")),
    (r"\alpha_{\beta'}'", Symbol("\\alpha_{\\beta'}'")),
    (r"\alpha_{\beta''}'", Symbol("\\alpha_{\\beta''}'")),
    (r"\alpha'_\beta'", Symbol("\\alpha'_{\\beta}'")),
    (r"\alpha'_{\beta}'", Symbol("\\alpha'_{\\beta}'")),
    (r"\alpha'_{\beta'}'", Symbol("\\alpha'_{\\beta'}'")),
    (r"\alpha'_{\beta''}'", Symbol("\\alpha'_{\\beta''}'")),
    (r"\alpha''_\beta'", Symbol("\\alpha''_{\\beta}'")),
    (r"\alpha''_{\beta}'", Symbol("\\alpha''_{\\beta}'")),
    (r"\alpha''_{\beta'}'", Symbol("\\alpha''_{\\beta'}'")),
    (r"\alpha''_{\beta''}'", Symbol("\\alpha''_{\\beta''}'")),
    (r"\alpha_\beta''", Symbol("\\alpha_{\\beta}''")),
    (r"\alpha_{\beta}''", Symbol("\\alpha_{\\beta}''")),
    (r"\alpha_{\beta'}''", Symbol("\\alpha_{\\beta'}''")),
    (r"\alpha_{\beta''}''", Symbol("\\alpha_{\\beta''}''")),
    (r"\alpha'_\beta''", Symbol("\\alpha'_{\\beta}''")),
    (r"\alpha'_{\beta}''", Symbol("\\alpha'_{\\beta}''")),
    (r"\alpha'_{\beta'}''", Symbol("\\alpha'_{\\beta'}''")),
    (r"\alpha'_{\beta''}''", Symbol("\\alpha'_{\\beta''}''")),
    (r"\alpha''_\beta''", Symbol("\\alpha''_{\\beta}''")),
    (r"\alpha''_{\beta}''", Symbol("\\alpha''_{\\beta}''")),
    (r"\alpha''_{\beta'}''", Symbol("\\alpha''_{\\beta'}''")),
    (r"\alpha''_{\beta''}''", Symbol("\\alpha''_{\\beta''}''"))

]

SIMPLE_EXPRESSION_PAIRS = [
    (r"0", 0),
    (r"1", 1),
    (r"-3.14", -3.14),
    (r"(-7.13)(1.5)", _Mul(-7.13, 1.5)),
    (r"1+1", _Add(1, 1)),
    (r"0+1", _Add(0, 1)),
    (r"1*2", _Mul(1, 2)),
    (r"0*1", _Mul(0, 1)),
    (r"x", x),
    (r"2x", 2 * x),
    (r"3x - 1", _Add(_Mul(3, x), -1)),
    (r"-c", -c),
    (r"\infty", oo),
    (r"a \cdot b", a * b),
    (r"1 \times 2 ", _Mul(1, 2)),
    (r"a / b", a / b),
    (r"a \div b", a / b),
    (r"a + b", a + b),
    (r"a + b - a", _Add(a + b, -a)),
    (r"(x + y) z", _Mul(_Add(x, y), z)),
    (r"a'b+ab'", _Add(_Mul(Symbol("a'"), b), _Mul(a, Symbol("b'"))))
]

FRACTION_EXPRESSION_PAIRS = [
    (r"\frac{a}{b}", a / b),
    (r"\dfrac{a}{b}", a / b),
    (r"\tfrac{a}{b}", a / b),
    (r"\frac{\sqrt{a}}{b}", sqrt(a) / b),
    (r"\frac12", Rational(1, 2)),
    (r"\frac12y", y / 2),
    (r"\frac1234", 17),
    (r"\frac2{3}", Rational(2, 3)),
    (r"\frac{a + b}{c}", (a + b) / c),
    (r"\frac{7}{3}", Rational(7, 3))
]

RELATION_EXPRESSION_PAIRS = [
    (r"x = y", Eq(x, y)),
    (r"x \neq y", Ne(x, y)),
    (r"x < y", Lt(x, y)),
    (r"x > y", Gt(x, y)),
    (r"x \leq y", Le(x, y)),
    (r"x \geq y", Ge(x, y)),
    (r"x <= y", Le(x, y)),
    (r"x \ge y", Ge(x, y)),
    (r"x < y", StrictLessThan(x, y)),
    (r"x \leq y", LessThan(x, y)),
    (r"x > y", StrictGreaterThan(x, y)),
    (r"x \geq y", GreaterThan(x, y)),
    (r"x \neq y", Unequality(x, y)), # same as 2nd one in the list
    (r"a^2 + b^2 = c^2", Eq(a**2 + b**2, c**2))
]

POWER_EXPRESSION_PAIRS = [
    (r"x^2", x ** 2),
    (r"x^\frac{1}{2}", sqrt(x)),
    (r"x^{3 + 1}", x ** 4),
    (r"\pi^{|xy|}", Symbol('pi') ** _Abs(x * y)),
    (r"5^0 - 4^0", 0)
]

INTEGRAL_EXPRESSION_PAIRS = [
    (r"\int x dx", Integral(x, x)),
    (r"\int x \, dx", Integral(x, x)),
    (r"\int x d\theta", Integral(x, theta)),
    (r"\int (x^2 - y)dx", Integral(x ** 2 - y, x)),
    (r"\int x + a dx", Integral(x + a, x)),
    (r"\int da", Integral(1, a)),
    (r"\int_0^7 dx", Integral(1, (x, 0, 7))),
    (r"\int\limits_{0}^{1} x dx", Integral(x, (x, 0, 1))),
    (r"\int_a^b x dx", Integral(x, (x, a, b))),
    (r"\int^b_a x dx", Integral(x, (x, a, b))),
    (r"\int_{a}^b x dx", Integral(x, (x, a, b))),
    (r"\int^{b}_a x dx", Integral(x, (x, a, b))),
    (r"\int_{a}^{b} x dx", Integral(x, (x, a, b))),
    (r"\int^{b}_{a} x dx", Integral(x, (x, a, b))),
    (r"\int_{f(a)}^{f(b)} f(z) dz", Integral(f(z), (z, f(a), f(b)))),
    (r"\int a + b + c dx", Integral(a + b + c, x)),
    # TODO: the below two were rewritten so the dz term is not in the fraction numerator.
    # it should be possible for them to be in the numerator, but the integral grammar has to be a bit more elaborate.
    (r"\int \frac{1}{z} dz", Integral(Pow(z, -1), z)),
    (r"\int \frac{3}{z} dz", Integral(3 * Pow(z, -1), z)),
    (r"\int \frac{1}{x} dx", Integral(1 / x, x)),
    (r"\int \frac{1}{a} + \frac{1}{b} dx", Integral(1 / a + 1 / b, x)),
    (r"\int \frac{1}{a} - \frac{1}{b} dx", Integral(1 / a - 1 / b, x)),
    (r"\int \frac{1}{x} + 1 dx", Integral(1 / x + 1, x))
]

DERIVATIVE_EXPRESSION_PAIRS = [
    (r"\frac{d}{dx} x", Derivative(x, x)),
    (r"\frac{d}{dt} x", Derivative(x, t)),
    (r"\frac{d}{dx^2} x^3", Derivative(x**3, (x, 2))),
    (r"\frac{d x y}{dx d y}", Derivative(x*y, (x, 1), (y, 1))),
    (r"\frac{d}{dx} ( \tan x )", Derivative(tan(x), x)),
    (r"\frac{d f(x)}{dx}", Derivative(f(x), x)),
    (r"\frac{d\theta(x)}{dx}", Derivative(Function('theta')(x), x))
]

TRIGONOMETRIC_EXPRESSION_PAIRS = [
    (r"\sin \theta", sin(theta)),
    (r"\sin(\theta)", sin(theta)),
    (r"\sin^{-1} a", asin(a)),
    (r"\sin a \cos b", _Mul(sin(a), cos(b))),
    (r"\sin \cos \theta", sin(cos(theta))),
    (r"\sin(\cos \theta)", sin(cos(theta))),
    (r"(\csc x)(\sec y)", csc(x) * sec(y)),
    (r"\frac{\sin{x}}2", _Mul(sin(x), _Pow(2, -1)))
]

UNEVALUATED_LIMIT_EXPRESSION_PAIRS = [
    (r"\lim_{x \to 3} a", Limit(a, x, 3, dir="+-")),
    (r"\lim_{x \rightarrow 3} a", Limit(a, x, 3, dir="+-")),
    (r"\lim_{x \Rightarrow 3} a", Limit(a, x, 3, dir="+-")),
    (r"\lim_{x \longrightarrow 3} a", Limit(a, x, 3, dir="+-")),
    (r"\lim_{x \Longrightarrow 3} a", Limit(a, x, 3, dir="+-")),
    (r"\lim_{x \to 3^{+}} a", Limit(a, x, 3, dir="+")),
    (r"\lim_{x \to 3^{-}} a", Limit(a, x, 3, dir="-")),
    (r"\lim_{x \to 3^+} a", Limit(a, x, 3, dir="+")),
    (r"\lim_{x \to 3^-} a", Limit(a, x, 3, dir="-")),
    (r"\lim_{x \to \infty} \frac{1}{x}", Limit(_Mul(1, _Pow(x, -1)), x, oo))
]

EVALUATED_LIMIT_EXPRESSION_PAIRS = [
    (r"\lim_{x \to \infty} \frac{1}{x}", Limit(1 / x, x, oo))
]

SQRT_EXPRESSION_PAIRS = [
    (r"\sqrt{x}", sqrt(x)),
    (r"\sqrt{x + b}", sqrt(x + b)),
    (r"\sqrt[3]{\sin x}", root(sin(x), 3)),
    (r"\sqrt[y]{\sin x}", root(sin(x), y)),
    (r"\sqrt[\theta]{\sin x}", root(sin(x), theta)),
    (r"\sqrt{\frac{12}{6}}", sqrt(2))
]

FACTORIAL_EXPRESSION_PAIRS = [
    (r"x!", factorial(x)),
    (r"100!", factorial(100)),
    (r"\theta!", factorial(theta)),
    (r"(x + 1)!", factorial(x + 1)),
    (r"(x!)!", factorial(factorial(x))),
    (r"x!!!", factorial(factorial(factorial(x)))),
    (r"5!7!", factorial(5) * factorial(7)),
    (r"24! \times 24!", factorial(24) * factorial(24))
]

SUM_EXPRESSION_PAIRS = [
    (r"\sum_{k = 1}^{3} c", Sum(c, (k, 1, 3))),
    (r"\sum_{k = 1}^3 c", Sum(c, (k, 1, 3))),
    (r"\sum^{3}_{k = 1} c", Sum(c, (k, 1, 3))),
    (r"\sum^3_{k = 1} c", Sum(c, (k, 1, 3))),
    (r"\sum_{k = 1}^{10} k^2", Sum(k ** 2, (k, 1, 10))),
    (r"\sum_{n = 0}^{\infty} \frac{1}{n!}", Sum(1 / factorial(n), (n, 0, oo)))
]

UNEVALUATED_PRODUCT_EXPRESSION_PAIRS = [
    (r"\prod_{a = b}^{c} x", Product(x, (a, b, c))),
    (r"\prod_{a = b}^c x", Product(x, (a, b, c))),
    (r"\prod^{c}_{a = b} x", Product(x, (a, b, c))),
    (r"\prod^c_{a = b} x", Product(x, (a, b, c)))
]

APPLIED_FUNCTION_EXPRESSION_PAIRS = [
    (r"f(x)", f(x)),
    (r"f(x, y)", f(x, y)),
    (r"f(x, y, z)", f(x, y, z)),
    (r"f'_1(x)", Function("f_{1}'")(x)),
    (r"f_{1}''(x+y)", Function("f_{1}''")(x + y)),
    (r"h_{\theta}(x_0, x_1)",
     Function('h_{\\theta}')(Symbol('x_{0}'), Symbol('x_{1}')))
]

COMMON_FUNCTION_EXPRESSION_PAIRS = [
    (r"|{x}|", Abs(x)),
    (r"|x|", Abs(x)),
    (r"||x||", Abs(Abs(x))),
    (r"|x| |y|", Abs(x) * Abs(y)),
    (r"|{|x| |y|}|", Abs(Abs(x) * Abs(y))),
    (r"\lfloor x \rfloor", floor(x)),
    (r"\lceil x \rceil", ceiling(x)),
    (r"\exp x", exp(x)),
    (r"\exp(x)", exp(x)),
    (r"\lg x", log(x, 10)),
    (r"\ln x", log(x)),
    (r"\ln xy", log(xy)),
    (r"\log x", log(x)),
    (r"\log xy", log(xy)),
    (r"\log_{2} x", log(x, 2)),
    (r"\log_{a} x", log(x, a)),
    (r"\log_{11} x", log(x, 11)),
    (r"\log_{a^2} x", log(x, _Pow(a, 2))),
    (r"\log_2 x", log(x, 2)),
    (r"\log_a x", log(x, a)),
    (r"\overline{z}", conjugate(z)),
    (r"\overline{\overline{z}}", conjugate(conjugate(z))),
    (r"\overline{x + y}", conjugate(x + y)),
    (r"\overline{x} + \overline{y}", conjugate(x) + conjugate(y)),
    (r"\min(a, b)", Min(a, b)),
    (r"\min(a, b, c - d, xy)", Min(a, b, c - d, xy)),
    (r"\max(a, b)", Max(a, b)),
    (r"\max(a, b, c - d, xy)", Max(a, b, c - d, xy)),
]

SPACING_RELATED_EXPRESSION_PAIRS = [
    (r"a \, b", _Mul(a, b)),
    (r"a \thinspace b", _Mul(a, b)),
    (r"a \: b", _Mul(a, b)),
    (r"a \medspace b", _Mul(a, b)),
    (r"a \; b", _Mul(a, b)),
    (r"a \thickspace b", _Mul(a, b)),
    (r"a \quad b", _Mul(a, b)),
    (r"a \qquad b", _Mul(a, b)),
    (r"a \! b", _Mul(a, b)),
    (r"a \negthinspace b", _Mul(a, b)),
    (r"a \negmedspace b", _Mul(a, b)),
    (r"a \negthickspace b", _Mul(a, b))
]

BINOMIAL_EXPRESSION_PAIRS = [
    (r"\binom{n}{k}", binomial(n, k)),
    (r"\tbinom{n}{k}", binomial(n, k)),
    (r"\dbinom{n}{k}", binomial(n, k)),
    (r"\binom{n}{0}", binomial(n, 0)),
    (r"x^\binom{n}{k}", x ** binomial(n, k))
]

MISCELLANEOUS_EXPRESSION_PAIRS = [
    (r"\left(x + y\right) z", _Mul(_Add(x, y), z)),
    (r"\left( x + y\right ) z", _Mul(_Add(x, y), z)),
    (r"\left(  x + y\right ) z", _Mul(_Add(x, y), z)),
]

UNEVALUATED_LITERAL_COMPLEX_NUMBER_EXPRESSION_PAIRS = [
    (r"i^2", _Pow(I, 2)),
    (r"|i|", _Abs(I)),
    (r"\overline{i}", _Conjugate(I)),
    (r"i+i", _Add(I, I)),
    (r"i-i", _Add(I, -I)),
    (r"i*i", _Mul(I, I)),
    (r"i/i", _Mul(I, _Pow(I, -1))),
    (r"(1+i)/|1+i|", _Mul(_Add(1, I), _Pow(_Abs(_Add(1, I)), -1)))
]

MATRIX_EXPRESSION_PAIRS = [
    (r"\det\left(\left[   \begin{array}{cc}a&b\\x&y\end{array} \right]\right)",
     Matrix([[a, b], [x, y]]).det()),
    (r"\det \begin{pmatrix}1&2\\3&4\end{pmatrix}", -2),
    (r"\det{\begin{pmatrix}1&2\\3&4\end{pmatrix}}", -2),
    (r"\det(\begin{pmatrix}1&2\\3&4\end{pmatrix})", -2),
    (r"\det\left(\begin{pmatrix}1&2\\3&4\end{pmatrix}\right)", -2),
    (r"\begin{pmatrix}a & b \\x & y\end{pmatrix}/\begin{vmatrix}a & b \\x & y\end{vmatrix}",
     _MatMul(Matrix([[a, b], [x, y]]), _Pow(Matrix([[a, b], [x, y]]).det(), -1))),
    (r"\begin{pmatrix}a & b \\x & y\end{pmatrix}/|\begin{matrix}a & b \\x & y\end{matrix}|",
     _MatMul(Matrix([[a, b], [x, y]]), _Pow(Matrix([[a, b], [x, y]]).det(), -1))),
    (r"\frac{\begin{pmatrix}a & b \\x & y\end{pmatrix}}{| { \begin{matrix}a & b \\x & y\end{matrix} } |}",
     _MatMul(Matrix([[a, b], [x, y]]), _Pow(Matrix([[a, b], [x, y]]).det(), -1))),
    (r"\overline{\begin{pmatrix}i & 1+i \\-i & 4\end{pmatrix}}",
     Matrix([[-I, 1-I], [I, 4]])),
    (r"\begin{pmatrix}i & 1+i \\-i & 4\end{pmatrix}^H",
     Matrix([[-I, I], [1-I, 4]])),
    (r"\operatorname{\trace}(\begin{pmatrix}i & 1+i \\-i & 4\end{pmatrix})",
     Trace(Matrix([[I, 1+I], [-I, 4]]))),
    (r"\operatorname{\adjugate}(\begin{pmatrix}1 & 2 \\3 & 4\end{pmatrix})",
     Matrix([[4, -2], [-3, 1]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^\ast",
     Matrix([[-2*I, 6], [4, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\ast}",
     Matrix([[-2*I, 6], [4, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\ast\ast}",
     Matrix([[2*I, 4], [6, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\ast\ast\ast}",
     Matrix([[-2*I, 6], [4, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{*}",
     Matrix([[-2*I, 6], [4, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{**}",
     Matrix([[2*I, 4], [6, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{***}",
     Matrix([[-2*I, 6], [4, 8]])),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^\prime",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\prime}",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\prime\prime}",
     _MatAdd(Matrix([[I, 2], [3, 4]]),
             Matrix([[I, 2], [3, 4]]))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{\prime\prime\prime}",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{'}",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{''}",
     _MatAdd(Matrix([[I, 2], [3, 4]]),
             Matrix([[I, 2], [3, 4]]))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^{'''}",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})'",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})''",
     _MatAdd(Matrix([[I, 2], [3, 4]]),
             Matrix([[I, 2], [3, 4]]))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})'''",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"\det(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})",
     (_MatAdd(Matrix([[I, 2], [3, 4]]),
              Matrix([[I, 2], [3, 4]]))).det()),
    (r"\mathrm{\trace}(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})",
     Trace(_MatAdd(Matrix([[I, 2], [3, 4]]),
                   Matrix([[I, 2], [3, 4]])))),
    (r"\mathrm{\adjugate}(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})",
     (Matrix([[8, -4], [-6, 2*I]]))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^T",
     Transpose(_MatAdd(Matrix([[I, 2], [3, 4]]),
                       Matrix([[I, 2], [3, 4]])))),
    (r"(\begin{pmatrix}i&2\\3&4\end{pmatrix}+\begin{pmatrix}i&2\\3&4\end{pmatrix})^H",
     (Matrix([[-2*I, 6], [4, 8]])))
]


def test_symbol_expressions():
    expected_failures = {6, 7}
    for i, (latex_str, sympy_expr) in enumerate(SYMBOL_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


def test_simple_expressions():
    expected_failures = {20}
    for i, (latex_str, sympy_expr) in enumerate(SIMPLE_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str

def test_fraction_expressions():
    for latex_str, sympy_expr in FRACTION_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_relation_expressions():
    for latex_str, sympy_expr in RELATION_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str

def test_power_expressions():
    expected_failures = {3}
    for i, (latex_str, sympy_expr) in enumerate(POWER_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


def test_integral_expressions():
    expected_failures = {14}
    for i, (latex_str, sympy_expr) in enumerate(INTEGRAL_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert simplify(parse_latex_lark(latex_str)) == simplify(sympy_expr.doit()), latex_str


def test_derivative_expressions():
    expected_failures = {5, 6}
    for i, (latex_str, sympy_expr) in enumerate(DERIVATIVE_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_trigonometric_expressions():
    expected_failures = {3}
    for i, (latex_str, sympy_expr) in enumerate(TRIGONOMETRIC_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_limit_expressions():
    for latex_str, sympy_expr in UNEVALUATED_LIMIT_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_square_root_expressions():
    for latex_str, sympy_expr in SQRT_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_factorial_expressions():
    for latex_str, sympy_expr in FACTORIAL_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str

def test_sum_expressions():
    for latex_str, sympy_expr in SUM_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


def test_product_expressions():
    for latex_str, sympy_expr in UNEVALUATED_PRODUCT_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str

def test_applied_function_expressions():
    expected_failures = {3, 4}  # 0 is ambiguous, and the others require not-yet-added features
    # not sure why 1, and 2 are failing
    for i, (latex_str, sympy_expr) in enumerate(APPLIED_FUNCTION_EXPRESSION_PAIRS):
        if i in expected_failures:
            continue
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_common_function_expressions():
    for latex_str, sympy_expr in COMMON_FUNCTION_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


# unhandled bug causing these to fail
def test_spacing():
    for latex_str, sympy_expr in SPACING_RELATED_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


def test_binomial_expressions():
    for latex_str, sympy_expr in BINOMIAL_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == sympy_expr, latex_str


def test_miscellaneous_expressions():
    for latex_str, sympy_expr in MISCELLANEOUS_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_literal_complex_number_expressions():
    for latex_str, sympy_expr in UNEVALUATED_LITERAL_COMPLEX_NUMBER_EXPRESSION_PAIRS:
        assert parse_latex_lark(latex_str) == simplify(sympy_expr), latex_str


def test_matrix_expressions():
    for latex_str, sympy_expr in MATRIX_EXPRESSION_PAIRS:
        if isinstance(sympy_expr, Expr):
            sympy_expr = sympy_expr.doit()
        assert simplify(parse_latex_lark(latex_str)) == simplify(expand(sympy_expr)), latex_str