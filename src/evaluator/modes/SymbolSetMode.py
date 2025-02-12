from ObsimatClient import ObsimatClient
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from ObsimatEnvironment import ObsimatEnvironment

from ModeResponse import ModeResponse
from sympy import *
from typing import Any, TypedDict

SETS = [
    S.Complexes,
    S.Reals,
    Interval(0, oo),
    Interval(-oo, 0),
    S.Rationals,
    Interval(0, oo).intersect(S.Rationals),
    Interval(-oo, 0).intersect(S.Rationals),
    S.Integers,
    Interval(-oo, 0).intersect(S.Integers),
    S.Naturals,
    S.Naturals0,
    FiniteSet(0),
]

SET_TO_LATEX = {
    S.Complexes: "\\mathbb{C}",
    S.Reals: "\\mathbb{R}",
    Interval(0, oo): "\\mathbb{R}_+",
    Interval(-oo, 0): "\\mathbb{R}_-",
    S.Rationals: "\\mathbb{Q}",
    Interval(0, oo).intersect(S.Rationals): "\\mathbb{Q}_+",
    Interval(-oo, 0).intersect(S.Rationals): "\\mathbb{Q}_-",
    S.Integers: "\\mathbb{Z}",
    Interval(-oo, 0).intersect(S.Integers): "\\mathbb{Z}_-",
    S.Naturals: "\\mathbb{N}",
    S.Naturals0: "\\mathbb{N}_0",
    FiniteSet(0): "\\{0\\}",
}


class SymbolSetModeMessage(TypedDict):
    environment: ObsimatEnvironment

# generates an latex array of symbols and their belonging sets, based on the given environment.
async def symbolSetMode(message: SymbolSetModeMessage, response: ModeResponse):
    environment: ObsimatEnvironment = message['environment']
    
    set_symbols = {set: [] for set in SETS}

    # loop over sets and figure out which symbol belongs to which sets.
    
    for symbol in environment['symbols']:
        sympy_symbol = ObsimatEnvironmentUtils.create_sympy_symbol(symbol, environment)
        
        smallest_containing_set = None
        
        for set in SETS:
            
            set_contains_symbol = set.contains(sympy_symbol)
            
            if set_contains_symbol == True:
                smallest_containing_set = set

        if smallest_containing_set is not None:
            set_symbols[smallest_containing_set].append(symbol)
    
    await response.result(set_symbols)

# Convert a set_symbols object returned rom symbolSetMode, into a latex formatted list of symbols and their belonging sets.
def symbolSetModeFormatter(set_symbols: Any, status: str, metadata: dict) -> str:
    latex_sets = []
    
    for set, symbols in set_symbols.items():
        if len(symbols) > 0:
            latex_sets.append(f"{', '.join(symbols)} & \\in & {SET_TO_LATEX[set]}")
    
    return f"\\begin{{array}}{{rcl}}\n{" \\\\\n".join(latex_sets)}\n\\end{{array}}"
