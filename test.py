from sympy import *
from sympy.physics.units import *
from sympy.physics.units.systems import SI
from sympy.physics.units.systems.si import dimsys_SI

def findBestConvert(expr):
    fres = expr
    max_powers = sum(expr.as_poly().degree_list())
    
    # do it per term for Add objects
    
    if expr is Add:
        print("ADD OBJECT")
    
    for unit in [ SI._base_units, *SI.get_units_non_prefixed() ]:
        res = convert_to(expr, unit)

        if sum(res.as_poly().degree_list()) < max_powers:
            fres = res
            
    return fres

print("123")
