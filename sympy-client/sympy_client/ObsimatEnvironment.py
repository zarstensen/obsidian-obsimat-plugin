from typing import TypedDict

class FunctionDef(TypedDict):
    args: list[str]
    expr: str

## The ObsimatEnvironment type represents a dictionary
## parsed from a json encoded ObsimatEnvironment typescript class.
class ObsimatEnvironment(TypedDict):
    symbols: dict[str, list[str]]
    variables: dict[str, str]
    functions: dict[str, FunctionDef]

    units_system: str
    excluded_symbols: list[str]

    domain: str
