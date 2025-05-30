from sympy_client.UnitsUtils import UNIT_ALIAS_MAP
from sympy.physics.units.quantities import Quantity, PhysicalConstant
import pandas as pd

unit_aliases: dict[Quantity, set[str]] = dict()
constant_aliases: dict[Quantity, set[str]] = dict()

# Loop through all exported things in unit_definitions
for alias, unit in UNIT_ALIAS_MAP.items():
    
    if unit.is_prefixed:
        continue
    
    if isinstance(unit, PhysicalConstant):
        alias_dict = constant_aliases
    else:
        alias_dict = unit_aliases
    
    if unit not in alias_dict:
        alias_dict[unit] = set()
    
    if alias not in alias_dict[unit] and alias != str(unit):
        alias_dict[unit].add(alias)



unit_data = {
    "Unit": [str(unit) for unit in unit_aliases.keys()],
    "Aliases": ["<br/>".join(aliases) for aliases in unit_aliases.values()]
}

unit_table = pd.DataFrame(unit_data)

unit_table.sort_values(by="Unit", inplace=True)
print("\n### Supported Units\n")
print(unit_table.to_markdown(index=False))

constants_data = {
    "Constant": [str(unit) for unit in constant_aliases.keys()],
    "Aliases": ["<br/>".join(aliases) for aliases in constant_aliases.values()]
}

constants_table = pd.DataFrame(constants_data)
    
constants_table.sort_values(by="Constant", inplace=True)

print("\n### Supported Physical Constants\n")
print(constants_table.to_markdown(index=False))

