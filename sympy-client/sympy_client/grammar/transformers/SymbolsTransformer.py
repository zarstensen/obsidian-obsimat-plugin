from typing import Iterator
from lark import Token, Transformer, v_args
from sympy import *
from sympy.physics.units import Quantity

from sympy_client import UnitsUtils
from sympy_client.grammar.transformers.DefStoreBaseTransformer import DefStoreBaseTransformer

@v_args(inline=True)
class SymbolsTransformer(DefStoreBaseTransformer):
    
    def symbol(self, *symbol_strings: str) -> Symbol:
        return self.definition_store.deserialize_symbol(''.join(map(str, symbol_strings)))
    
    def indexed_symbol(self, symbol: Expr, index: Expr | str, primes: str | None) -> Symbol:
        primes = '' if primes is None else primes
        indexed_text = str(index)
        
        if not indexed_text.startswith('{') or not indexed_text.endswith('}'):
            indexed_text = f"{{{indexed_text}}}"
        
        return self.symbol(f"{symbol}_{indexed_text}{primes}")
    
    def formatted_symbol(self, formatter: Token, text: str, primes: str | None) -> Symbol:
        formatter_text = str(formatter)
        primes = '' if primes is None else primes
        
        return self.symbol(f"{formatter_text}{text}{primes}")

    @v_args(inline=False)
    def brace_surrounded_text(self, tokens):        
        return ''.join(map(str, tokens))
    
    def unit(self, unit_symbol: Symbol) -> Quantity | Symbol:
        unit = UnitsUtils.str_to_unit(str(unit_symbol))
        
        if unit is not None:
            return unit
        else:
            return self.symbol(unit_symbol)
        
    def substitute_symbol(self, symbol: Symbol) -> Symbol | Expr:
        substituted_value = self.definition_store.get_symbol_definition(symbol)
        
        if substituted_value is not None:
            return substituted_value.value
        else:
            return symbol
    
    def undefined_function(self, func_name: Token, func_args: Iterator[Expr]) -> Function | Expr:
        func_name = func_name.value[:-1] # remove the suffixed parenthesees
        func = self.definition_store.deserialize_function(func_name)
        
        func_definition = self.definition_store.get_function_definition(func)
        
        if func_definition:
            return func_definition.call(*func_args)
        else:
            return func(*func_args)
    