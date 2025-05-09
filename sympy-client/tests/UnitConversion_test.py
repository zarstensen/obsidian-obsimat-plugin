from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.command_handlers.EvalHandler import *
from sympy_client.command_handlers.ConvertUnitsHandler import *
from sympy_client.command_handlers.SolveHandler import *

from sympy import *
import sympy.physics.units as units


## Tests the unit conversions.
class TestUnitConversion:
    parser = ObsimatLatexParser()
    
    def test_single_term_to_derived_unit(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "kg * m / s^2", "environment": { "units_system": "SI" }})

        assert result.sympy_expr.rhs == units.newton
        
    def test_single_term_to_base_units(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J / m * s^2", "environment": { "units_system": "SI" }})
        
        assert result.sympy_expr.rhs == units.kilogram * units.meter
    
    
    def test_multiple_terms(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J / m * s^2 + kg * m / s^2", "environment": { "units_system": "SI" }})
        
        assert result.sympy_expr.rhs == units.kilogram * units.meter + units.newton
    
    def test_excluded_units(self):
        J = symbols("J")
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J * kg * m / s^2", "environment": { "units_system": "SI", "excluded_symbols": ["J"] }})
        
        assert result.sympy_expr.rhs == J * units.newton
      
    def test_explicit_conversion(self):
        handler = ConvertUnitsHandler(self.parser)
        result = handler.handle({"expression": "7.2 * km / h", "target_units": ["m", "s"], "environment": {}})
        
        assert result.sympy_expr.rhs == 2.0 * units.meter / units.second
        
    def test_solve_conversion(self):
        handler = SolveHandler(self.parser)
        result = handler.handle({"expression": "2 x = 50 kg", "environment": { "units_system": "SI" }})
        
        assert result.solution == FiniteSet(25 * units.kilogram)
        
    def test_units_in_matrix(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({
            "expression": r"""
                km
                \begin{bmatrix}
                1 km \\
                2 s/km \\
                3 N
                \end{bmatrix}
            """,
            "environment": {"units_system": "SI"}
        })
        
        assert result.sympy_expr.rhs == Matrix([units.kilometer**2, 2 * units.second, 3000 * units.joule])
        
    def test_units_not_in_system(self):
        A = symbols('A')
        
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "A", "environment": { "units_system": "MKS" }})
        
        assert result.sympy_expr == A
        
    def test_simplification(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"\sqrt{ s^2 }", "environment": { "units_system": "MKS" }})

        assert result.sympy_expr.rhs == units.second
        
