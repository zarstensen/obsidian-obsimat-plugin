from typing import TypedDict

## The ObsimatEnvironment type represents a dictionary
## parsed from a json encoded ObsimatEnvironment typescript class.
class ObsimatEnvironment(TypedDict):
    symbols: dict[str, list[str]]
    variables: dict[str, str]

    units_enabled: bool
    excluded_units: list[str]

    domain: str
