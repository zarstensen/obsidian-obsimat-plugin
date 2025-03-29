from grammar.SystemOfExpr import SystemOfExpr

import sympy.physics.units as u
from sympy.physics.units.quantities import Quantity 
from sympy.physics.units.systems import SI
from sympy import *
from ObsimatEnvironment import ObsimatEnvironment

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
        
        # check if any symbol matches a unit string
        for symbol in sympy_expr.free_symbols:
            if 'excluded_units' in environment and str(symbol) in environment['excluded_units']:
                continue
            
            # attempt to replace the symbol with a corresponding unit.
            try:
                units = u.find_unit(str(symbol))
                if units[0] == str(symbol):
                    sympy_expr = sympy_expr.subs({symbol: getattr(u, units[0])})
            except AttributeError:
                # unit was not found.
                continue
        
        if not isinstance(sympy_expr, Add):
            sympy_expr = [sympy_expr]
        else:
            sympy_expr = list(sympy_expr.args)
        
        converted_expressions = []
        
        for expr in sympy_expr:
            curr_complexity = ObsimatEnvironmentUtils._get_unit_complexity(expr)
            
            # Conver to using all base units of system.
            for units in [ SI._base_units, *SI.get_units_non_prefixed() ]:
                converted_expr = u.convert_to(expr, units)
                converted_expr_complexity = ObsimatEnvironmentUtils._get_unit_complexity(converted_expr)
                
                if converted_expr_complexity < curr_complexity:
                    curr_complexity = converted_expr_complexity
                    expr = converted_expr

            converted_expressions.append(expr)

        return Add(*converted_expressions)

    @staticmethod
    def _get_unit_complexity(expression):
        complexity = 0
        
        for val, pow in expression.as_powers_dict().items():
            if isinstance(val, Quantity):
                
                if 0 < abs(pow) < 1:
                    pow = 1 / pow
                
                complexity += abs(pow)
                
        return complexity