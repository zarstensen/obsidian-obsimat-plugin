from lark import Token, v_args, Discard
from sympy import Expr, Symbol, FiniteSet
from sympy_client.grammar.transformers.SymbolsTransformer import SymbolsTransformer

@v_args(inline=True)
class SymbolsOnlyTransformer(SymbolsTransformer):
    
    def latex_string(self, symbols: list[Symbol] = []) -> FiniteSet:
        return FiniteSet(*symbols)
    
    def __default__(self, data, children, meta):
        
        symbols = [ ]
        
        for child in children:
            if child is None or isinstance(child, Token):
                continue
            elif isinstance(child, list) or isinstance(child, tuple):
                symbols.extend(child)
            else:
                symbols.append(child)
        
        if len(symbols) == 0:
            return Discard
        
        return symbols
    
    def substitute_symbol(self, symbol: Symbol) -> Symbol | Expr:
        return symbol