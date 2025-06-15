import sympy.physics.units as u
from sympy import *
from sympy_client.command_handlers.SolveHandler import *
from sympy_client.grammar.LatexCompiler import LatexSympyCompiler


class TestSolve:
    parser = LatexSympyCompiler
    
    def test_solve_with_domain(self):
        x = symbols('x')
        
        handler = SolveHandler(self.parser)
        result = handler.handle({ "expression": r"\sin(x) = 0", "environment": { "domain": "Interval.Ropen(0, 2 * pi)"} })
        
        assert result.symbols == [x]
        assert result.solution == FiniteSet(0, pi)
        
    def test_solve_soe(self):
        x, y, z = symbols('x y z')
        
        handler = SolveHandler(self.parser)
        
        result = handler.handle({
            "expression": r"""
            \begin{align}
            x + y + z & = 5 \\
            2x + 5z & = 10 \\
            2y + x & = 3 \\
            \end{align}
            """,
            "environment": {}
        })
        
        assert result.solution == FiniteSet((15, -6, -4))
        assert result.symbols == [x, y, z]
        
        result = handler.handle({
            "expression": r"""
            \begin{align}
            3 * x^2 & = 2 * y \\
            y &= \frac{3}{2} x \\
            \end{align}
            """,
            "environment": {}
        })
        
        assert result.solution == FiniteSet((0, 0), (1, Rational(3, 2)))
        assert result.symbols == [x, y]
    
    def test_solve_multivariate(self):
        x, y, z = symbols('x y z')
        
        handler = SolveHandler(self.parser)
        
        result = handler.handle({
            "expression": r"""
            \begin{cases}
            x + y = z \\
            x - y = -z \\
            \end{cases}
            """,
            "symbols": ["x", "y"],
            "environment": {}
        })
        
        assert result.solution == FiniteSet((0, z))
        assert result.symbols == [x, y]
        
        result = handler.handle({
            "expression": r"""
            \begin{cases}
            x + y = z \\
            x - y = -z \\
            \end{cases}
            """,
            "symbols": ["y", "z"],
            "environment": {}
        })
        
        assert result.solution == EmptySet
        assert result.symbols == [y, z]

    def test_solve_simplify(self):
        handler = SolveHandler(self.parser)
        
        result = handler.handle({ "expression": r"x^2 = 5 {kW} {h}", "environment": { } })
        
        assert result.solution == FiniteSet(sqrt(5 * 3600000 * u.joule), -sqrt(5 * 3600000 * u.joule))