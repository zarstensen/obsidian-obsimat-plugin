from grammar.ObsimatLatexParser import ObsimatLatexParser
from tests.TestResponse import TestResponse
from modes.EvalMode import eval_handler
from modes.EvalfMode import evalf_handler
from modes.FactorMode import factor_handler
from modes.ExpandMode import expand_handler
from modes.ApartMode import apart_handler
import asyncio

from sympy import *
import sympy.physics.units as units


## Tests the unit conversions.
class TestUnitConversion:
    parser = ObsimatLatexParser()
    
    def test_single_term_to_derived_unit(self):
        response = TestResponse()
        asyncio.run(eval_handler({"expression": "kg * m / s^2", "environment": { "units_enabled": True }}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()['result'].rhs
            
        assert result == units.newton
        
    def test_single_term_to_base_units(self):
        response = TestResponse()
        asyncio.run(eval_handler({"expression": "J / m * s^2", "environment": { "units_enabled": True }}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()['result'].rhs
            
        assert result == units.kilogram * units.meter
    
    
    def test_multiple_terms(self):
        response = TestResponse()
        asyncio.run(eval_handler({"expression": "J / m * s^2 + kg * m / s^2 ", "environment": { "units_enabled": True }}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()['result'].rhs
            
        assert result == units.kilogram * units.meter + units.newton
    
    def test_exluded_units(self):
        J = symbols("J")
        response = TestResponse()
        asyncio.run(eval_handler({"expression": "J * kg * m / s^2 ", "environment": { "units_enabled": True, "excluded_units": ["J"] }}, response, self.parser))
        assert response.hasResult()
        
        result = response.getResult()['result'].rhs
        
        assert result == J * units.newton