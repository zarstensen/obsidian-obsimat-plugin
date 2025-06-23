from sympy import *
from sympy.physics.units import convert_to

import sympy_client.UnitsUtils as UnitsUtils

from .EvalHandlerBase import EvalHandlerBase, EvalResult, EvaluateMessage


class ConvertMessage(EvaluateMessage):
    target_units: list[str]

# Tries to convert the sympy expressions units to the provided units in message.target_units.
class ConvertUnitsHandler(EvalHandlerBase):

    def handle(self, message: ConvertMessage) -> EvalResult:
        message['environment']['unit_system'] = "SI"
        return super().handle(message)

    def evaluate(self, sympy_expr: Expr, message: ConvertMessage):
        if 'target_units' not in message:
            return sympy_expr

        target_units = []

        for target_unit_str in message['target_units']:
            target_unit = UnitsUtils.str_to_unit(target_unit_str)

            if target_unit is not None:
                target_units.append(target_unit)

        sympy_expr = convert_to(sympy_expr, target_units)

        return sympy_expr
