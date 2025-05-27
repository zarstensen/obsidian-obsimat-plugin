from sympy import Add, Matrix, MatrixBase, Symbol
import sympy.physics.units as u
from sympy.physics.units.quantities import Quantity 
from sympy.physics.units.systems import SI
from sympy.physics.units.unitsystem import UnitSystem

# Substitute any symbols present in the sympy expression with the corresponding sympy unit.
# Also convert all non base units to base units where possible.
def substitute_units(sympy_expr, excluded_symbols: list[Symbol], unit_system: UnitSystem):
    # check if any symbol matches a unit string
    for symbol in sympy_expr.free_symbols:
        if symbol in excluded_symbols:
            continue
        
        # attempt to replace the symbol with a corresponding unit.
        try:
            # find potential unit
            found_units = u.find_unit(str(symbol))
            
            if len(found_units) <= 0:
                continue
            
            unit_str = found_units[0]
            
            if unit_str != str(symbol):
                continue
            
            unit = getattr(u, unit_str)
            
            # check if the unit is in the passed unit system
            converted_units = u.convert_to(unit, unit_system._base_units)
            converted_units = (q for q in converted_units.as_terms()[1] if isinstance(q, Quantity))
            
            
            for q in converted_units:
                if q not in unit_system._base_units:
                    break
            else:
                # substitute the unit in for the symbol
                sympy_expr = sympy_expr.subs({symbol: unit})
            
        except AttributeError:
            # unit was not found.
            continue
        
    return sympy_expr

# attempt to automatically convert the units in the given sympy expression.
# this convertion method prioritizes as few units as possible raised to the lowest power possible (or lowest root possible).
def auto_convert(sympy_expr, unit_system: UnitSystem):
    if unit_system is None:
        unit_system = SI
    
    if isinstance(sympy_expr, MatrixBase):
        converted_matrix = Matrix.zeros(*sympy_expr.shape)
        for index, value in enumerate(sympy_expr):
            converted_matrix[index] = auto_convert(value, unit_system)
        
        return converted_matrix
    
    if not isinstance(sympy_expr, Add):
        sympy_expr = [sympy_expr]
    else:
        sympy_expr = list(sympy_expr.args)
    
    converted_expressions = []
    
    for expr in sympy_expr:
        curr_complexity = get_unit_complexity(expr)
        
        # Conver to using all base units of system.
        for units in [ unit_system._base_units, *unit_system.get_units_non_prefixed() ]:
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