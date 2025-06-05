from sympy_client.LmatEnvironment import LmatEnvironment
from .CommandHandler import *
from ..grammar.SymbolStore import SymbolStore

from sympy import *
from typing import TypedDict, override

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

class SymbolSetResult(CommandResult):
    def __init__(self, set_symbols: dict[Set, list[Symbol]]):
        super().__init__()
        self.set_symbols = set_symbols
    
    @override
    def getPayload(self) -> dict:
        latex_sets = []
    
        for set, symbols in self.set_symbols.items():
            if len(symbols) > 0:
                latex_sets.append(f"{', '.join(symbols)} & \\in & {SET_TO_LATEX[set]}")
        
        return CommandResult.result(f"\\begin{{array}}{{rcl}}\n{" \\\\\n".join(latex_sets)}\n\\end{{array}}")
        

class SymbolSetModeMessage(TypedDict):
    environment: LmatEnvironment

class SymbolSetHandler(CommandHandler):
    def handle(self, message: SymbolSetModeMessage) -> SymbolSetResult:
        environment: LmatEnvironment = message['environment']
        symbol_store: SymbolStore = SymbolStore(environment)
    
        set_symbols = {set: [] for set in SETS}

        # loop over sets and figure out which symbol belongs to which sets.        
        for symbol in environment.get('symbols', {}):
            sympy_symbol = symbol_store.get_symbol(symbol)
            
            smallest_containing_set = None
            
            for set in SETS:
                
                set_contains_symbol = set.contains(sympy_symbol)
                
                if set_contains_symbol == True:
                    smallest_containing_set = set

            if smallest_containing_set is not None:
                set_symbols[smallest_containing_set].append(symbol)
        
        return SymbolSetResult(set_symbols)
