from sympy_client.grammar.LmatLatexParser import LmatLatexParser
from sympy_client.command_handlers.EvalHandler import *
from sympy_client.command_handlers.ConvertUnitsHandler import *
from sympy_client.command_handlers.SolveHandler import *

from sympy import *
import sympy.physics.units as units


## Tests the unit conversions.
class TestUnitConversion:
    parser = LmatLatexParser()
    
    def test_single_term_to_derived_unit(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "kg * m / s^2", "environment": { "unit_system": "SI" }})

        assert result.sympy_expr == units.newton
        
    def test_single_term_to_base_units(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J / m * s^2", "environment": { "unit_system": "SI" }})
        
        assert result.sympy_expr == units.kilogram * units.meter
    
    
    def test_multiple_terms(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J / m * s^2 + kg * m / s^2", "environment": { "unit_system": "SI" }})
        
        assert result.sympy_expr == units.kilogram * units.meter + units.newton
    
    def test_excluded_units(self):
        J = symbols("J")
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "J * kg * m / s^2", "environment": { "unit_system": "SI", "excluded_symbols": ["J"] }})
        
        assert result.sympy_expr == J * units.newton
      
    def test_explicit_conversion(self):
        handler = ConvertUnitsHandler(self.parser)
        result = handler.handle({"expression": "7.2 * km / h", "target_units": ["m", "s"], "environment": {}})
        
        assert result.sympy_expr == 2.0 * units.meter / units.second
        
        result = handler.handle({"expression": "10 {gee}", "target_units": ["m", "s"], "environment": {}})
        assert result.sympy_expr - 98.06650 * units.meter / (units.seconds**2) < 1e-15 * units.meter / units.seconds**2
        
        result = handler.handle({"expression": "{gee}", "target_units": ["m", "s"], "environment": {}})
        print(result)
        
    def test_solve_conversion(self):
        handler = SolveHandler(self.parser)
        result = handler.handle({"expression": "2 x = 50 kg", "environment": { "unit_system": "SI" }})
        
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
            "environment": {"unit_system": "SI"}
        })
        
        assert result.sympy_expr == Matrix([units.kilometer**2, 2 * units.second, 3000 * units.joule])
        
    def test_units_not_in_system(self):
        A = symbols('A')
        
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": "A", "environment": { "unit_system": "MKS" }})
        
        assert result.sympy_expr == A
        
    def test_simplification(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"\sqrt{ s^2 }", "environment": { "unit_system": "MKS" }})

        assert result.sympy_expr == units.second

    def test_brace_units(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"\frac{{kg}\,{m}^{2}}{{s}^2}", "environment": {}})
        assert result.sympy_expr == units.joule
        
    def test_physical_constants(self):
        handler = EvalHandler(self.parser)
        result = handler.handle({"expression": r"5 {gee} \cdot (10 {minutes})^2", "environment": {}})
        assert result.sympy_expr == 17651970.0 * units.meters
        