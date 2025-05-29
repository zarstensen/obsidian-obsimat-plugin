from .grammar.SystemOfExpr import SystemOfExpr
from .LmatEnvironment import LmatEnvironment
from . import UnitsUtils

import sympy.physics.units as u
from sympy.physics.units.quantities import Quantity 
from sympy.physics.units.unitsystem import UnitSystem
from sympy.core.relational import Relational
from sympy import *

## The LmatEnvironmentUtils provide various utility functions for a math expression present in an LmatEnvironment.
class LmatEnvironmentUtils:
    
    # list of symbols which commonly are not interpreted as their equivalent unit.
    DEFAULT_EXCLUDED_UNIT_SYMBOLS = ['g', 'L']
    
    @staticmethod
    def create_sympy_symbol(symbol: str, environment: LmatEnvironment):
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
    def substitute_units(sympy_expr, environment: LmatEnvironment):
        if 'unit_system' not in environment:
            # still perform auto convert, but with default unit system instead.
            return UnitsUtils.auto_convert(sympy_expr)
        
        unit_system_id_str = environment['unit_system']
        
        unit_system = UnitSystem.get_unit_system(unit_system_id_str)
        
        # substitute units recursively for all system of equations.
        if isinstance(sympy_expr, SystemOfExpr):
            for i in range(len(sympy_expr)):
                sympy_expr.change_expr(i, lambda e: LmatEnvironmentUtils.substitute_units(e, environment))
            
            return sympy_expr
        if isinstance(sympy_expr, Relational):
            lhs = LmatEnvironmentUtils.substitute_units(sympy_expr.lhs, environment)
            rhs = LmatEnvironmentUtils.substitute_units(sympy_expr.rhs, environment)
            return sympy_expr.func(lhs, rhs)
        
        if 'excluded_symbols' in environment:
            excluded_symbols = []
            for symbol_str in environment['excluded_symbols']:
                if 'symbols' in environment and symbol_str in environment['symbols']:
                    excluded_symbols.append(LmatEnvironmentUtils.create_sympy_symbol(symbol_str, environment))
                else:
                    excluded_symbols.append(Symbol(symbol_str))
        else:
            excluded_symbols = LmatEnvironmentUtils.DEFAULT_EXCLUDED_UNIT_SYMBOLS
        
        sympy_expr = UnitsUtils.substitute_units(sympy_expr, excluded_symbols, unit_system)
        sympy_expr = UnitsUtils.auto_convert(sympy_expr, unit_system)
        
        return sympy_expr
