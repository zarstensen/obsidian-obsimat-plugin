from sympy_client.modes.EvalModeBase import EvaluateMessage, eval_mode_base
from sympy_client.ModeResponse import ModeResponse
from sympy_client.grammar.SympyParser import SympyParser
from sympy.physics.units import convert_to
import sympy_client.UnitsUtils as UnitsUtils

from sympy import *

class ConvertMessage(EvaluateMessage):
    target_units: list[str]

## Tries to convert the sympy expressions units to the provided units in message.target_units.
async def convert_units_handler(message: ConvertMessage, response: ModeResponse, parser: SympyParser):
    def evaluate(sympy_expr):
        if 'target_units' not in message:
            return sympy_expr
        
        target_units = []
        
        for target_unit_str in message['target_units']:
            target_unit = UnitsUtils.str_to_unit(target_unit_str)
            
            if target_unit is not None:
                target_units.append(target_unit)
        
        sympy_expr = convert_to(sympy_expr, target_units)
        
        return sympy_expr
    
    # force units to be enabled, when converting between units.
    message['environment']['units_enabled'] = True
    
    return await eval_mode_base(message, response, parser, evaluate)
