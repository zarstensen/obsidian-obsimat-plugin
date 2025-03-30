from sympy import Add, Symbol
import sympy.physics.units as u
from sympy.physics.units.quantities import Quantity 
from sympy.physics.units.systems import SI

# Substitute any symbols present in the sympy expression with the corresponding sympy unit.
# Also convert all non base units to base units where possible.
def substitute_units(sympy_expr, excluded_symbols: list[Symbol]):
    # check if any symbol matches a unit string
    for symbol in sympy_expr.free_symbols:
        if symbol in excluded_symbols:
            continue
        
        # attempt to replace the symbol with a corresponding unit.
        try:
            units = u.find_unit(str(symbol))
            if units[0] == str(symbol):
                sympy_expr = sympy_expr.subs({symbol: getattr(u, units[0])})
        except AttributeError:
            # unit was not found.
            continue
        
    return sympy_expr

# attempt to automatically convert the units in the given sympy expression.
# this convertion method prioritizes as few units as possible raised to the lowest power possible (or lowest root possible).
def auto_convert(sympy_expr):
    if not isinstance(sympy_expr, Add):
        sympy_expr = [sympy_expr]
    else:
        sympy_expr = list(sympy_expr.args)
    
    converted_expressions = []
    
    for expr in sympy_expr:
        curr_complexity = get_unit_complexity(expr)
        
        # Conver to using all base units of system.
        for units in [ SI._base_units, *SI.get_units_non_prefixed() ]:
            converted_expr = u.convert_to(expr, units)
            converted_expr_complexity = get_unit_complexity(converted_expr)
            
            if converted_expr_complexity < curr_complexity:
                curr_complexity = converted_expr_complexity
                expr = converted_expr

        converted_expressions.append(expr)

    return Add(*converted_expressions)

# find sympy unit which has the given str representation.
def str_to_unit(unit_str) -> Quantity | None:
    # attempt to replace the symbol with a corresponding unit.
    try:
        units = u.find_unit(unit_str)
        if units[0] == unit_str:
            return getattr(u, units[0])
        else:
            return None
    except AttributeError:
        return None

# get the 'complexity' of a unit.
# complexity is defined as the sum of all units raised power (or 1/power if 0 < power < 1).
def get_unit_complexity(expression):
        complexity = 0
        
        for val, pow in expression.as_powers_dict().items():
            if isinstance(val, Quantity):
                
                if 0 < abs(pow) < 1:
                    pow = 1 / pow
                
                complexity += abs(pow)
                
        return complexity