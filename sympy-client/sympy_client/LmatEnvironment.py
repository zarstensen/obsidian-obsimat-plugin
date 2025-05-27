from typing import TypedDict

class FunctionDef(TypedDict):
    args: list[str]
    expr: str

## The LmatEnvironment type represents a dictionary
## parsed from a json encoded LmatEnvironment typescript class.
class LmatEnvironment(TypedDict):
    symbols: dict[str, list[str]]
    variables: dict[str, str]
    functions: dict[str, FunctionDef]

    unit_system: str
    excluded_symbols: list[str]

    domain: str
