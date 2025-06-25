from copy import copy

import sympy.physics.units as u
import sympy.physics.units.definitions.unit_definitions as unit_definitions
from sympy import Add, Expr, MatrixBase, Rel
from sympy.physics.units.quantities import PhysicalConstant, Quantity
from sympy.physics.units.systems import SI
from sympy.physics.units.unitsystem import UnitSystem

# Maps an alias to its corresponding Quantity object.
UNIT_ALIAS_MAP = {}

__defined_units_quantities = { unit_name: getattr(unit_definitions, unit_name) for unit_name in dir(unit_definitions) if isinstance(getattr(unit_definitions, unit_name), Quantity) }

def __add_unit_aliases(str_units: list[tuple[str, Quantity]]):
    for k, u in str_units:
        if k not in UNIT_ALIAS_MAP:
            UNIT_ALIAS_MAP[k] = u

# add SI units
__add_unit_aliases(( (str(unit), unit) for unit in SI._units))
__add_unit_aliases(( (str(unit.abbrev), unit) for unit in SI._units))

# add units specified in the defined_units module
__add_unit_aliases(((key, unit)
                for key, unit in __defined_units_quantities.items()
                if not isinstance(unit, PhysicalConstant)))

__add_unit_aliases(((str(unit.abbrev), unit)
                for unit in __defined_units_quantities.values()
                if not isinstance(unit, PhysicalConstant)))

__add_unit_aliases(((key, unit)
                for key, unit in __defined_units_quantities.items()
                if isinstance(unit, PhysicalConstant)))

__add_unit_aliases(((str(unit.abbrev), unit)
                for unit in __defined_units_quantities.values()
                if isinstance(unit, PhysicalConstant)))

# add LaTeX Math specific unit aliases.
__add_unit_aliases([ ( 'min', u.minute ), ( 'sec', u.second ) ])

# attempt to automatically convert the units in the given sympy expression.
# this convertion method prioritizes as few units as possible raised to the lowest power possible (or lowest root possible).
def auto_convert(sympy_expr, unit_system: UnitSystem = SI):
    if isinstance(sympy_expr, MatrixBase):
        new_matrix_contents = []

        for value in sympy_expr:

            new_matrix_contents.append(auto_convert(value, unit_system))

        return type(sympy_expr)(*sympy_expr.shape, new_matrix_contents)
    # relationals and non sympy objects should not be auto converted
    elif isinstance(sympy_expr, Rel) or not isinstance(sympy_expr, Expr):
        return sympy_expr

    if not isinstance(sympy_expr, Add):
        sympy_expr = [sympy_expr]
    else:
        sympy_expr = list(sympy_expr.args)

    converted_expressions = []

    for expr in sympy_expr:
        curr_complexity = get_unit_complexity(expr)

        # unit complexity cannot be determined for expression for some reason.
        if curr_complexity is None:
            converted_expressions.append(expr)
            continue

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
def str_to_unit(unit_str: str) -> Quantity | None:
    # attempt to replace the symbol with a corresponding unit.
    if unit_str not in UNIT_ALIAS_MAP:
        return None
    else:
        unit = copy(UNIT_ALIAS_MAP[unit_str])
        unit._latex_repr = unit_str
        return unit


# get the 'complexity' of a unit.
# complexity is defined as the sum of all units raised power (or 1/power if 0 < power < 1).
def get_unit_complexity(expression):

    if not hasattr(expression, 'as_powers_dict'):
        return None

    complexity = 0

    for val, pow in expression.as_powers_dict().items():
        if isinstance(val, Quantity):

            if 0 < abs(pow) < 1:
                pow = 1 / pow

            complexity += abs(pow)

    return complexity
