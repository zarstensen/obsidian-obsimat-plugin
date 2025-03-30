from grammar.SystemOfExpr import SystemOfExpr

import sympy.physics.units as u
from sympy.physics.units.quantities import Quantity 
from sympy.physics.units.systems import SI
from sympy import *
from ObsimatEnvironment import ObsimatEnvironment
import UnitsUtils

## The ObsimatEnvironmentUtils provide various utility functions for a math expression present in an ObsimatEnvironment.
class ObsimatEnvironmentUtils:
    
    @staticmethod
    def create_sympy_symbol(symbol: str, environment: ObsimatEnvironment):
        if str(symbol) not in environment['symbols']:
            raise ValueError(f"Symbol {symbol} not found in environment.")
        
        assumptions = {}
        for assumption in environment['symbols'][str(symbol)]:
            assumptions[assumption] = True
        
        # TODO: warn here if an assumption is not recognized.
        # create the sympy symbol here
        sympy_symbol = Symbol(str(symbol), **assumptions)
        
        return sympy_symbol
    
    # Substitute any symbols present in the sympy expression with the corresponding unit from the environment.
    # Also convert all non base units to base units where possible.
    @staticmethod
    def substitute_units(sympy_expr, environment: ObsimatEnvironment):
        if 'units_enabled' not in environment or not environment['units_enabled']:
            return sympy_expr
        
        # substitute units recursively for all system of equations.
        if isinstance(sympy_expr, SystemOfExpr):
            for i in range(len(sympy_expr)):
                sympy_expr.change_expr(i, lambda e: ObsimatEnvironmentUtils.substitute_units(e, environment))
            
            return sympy_expr
        
        excluded_symbols = []
        
        if 'excluded_symbols' in environment:
            for symbol_str in environment['excluded_symbols']:
                if 'symbols' in environment and symbol_str in environment['symbols']:
                    excluded_symbols.append(ObsimatEnvironmentUtils.create_sympy_symbol(symbol_str, environment))
                else:
                    excluded_symbols.append(Symbol(symbol_str))
        
        sympy_expr = UnitsUtils.substitute_units(sympy_expr, excluded_symbols)
        sympy_expr = UnitsUtils.auto_convert(sympy_expr)
        
        return sympy_expr
