from grammar.ObsimatLarkTransformer import ObsimatLarkTransformer

import sympy.physics.units as u
from sympy import *
from sympy.parsing.latex.lark import LarkLaTeXParser
import sympy.parsing.latex.lark as sympy_lark
from sympy.core import Expr
from typing import Any, Callable
from lark import Tree
from ObsimatEnvironment import ObsimatEnvironment
import regex
import os
from tempfile import TemporaryDirectory
import shutil

## The ObsimatEnvironmentUtils provide various utility functions for a math expression present in an ObsimatEnvironment.
class ObsimatEnvironmentUtils:
    
    @staticmethod
    def create_sympy_symbol(symbol: str, environment: ObsimatEnvironment):
        if str(symbol) not in environment['symbols']:
            raise ValueError(f"Symbol {symbol} not found in environment.")
        
        assumptions = {}
        for assumption in environment['symbols'][str(symbol)]:
            assumptions[assumption] = True
        
        # TODO: warn here if an assumption is not recognized.
        # create the sympy symbol here
        sympy_symbol = Symbol(str(symbol), **assumptions)
        
        return sympy_symbol
    
    # Substitute any symbols present in the sympy expression with the corresponding unit from the environment.
    # Also convert all non base units to base units where possible.
    # TODO: make this work with SystemOfExpr
    @staticmethod
    def substitute_units(sympy_expr, environment: ObsimatEnvironment):
        if 'units' not in environment:
            return sympy_expr
        
        # check if any symbol matches a unit string
        for symbol in sympy_expr.free_symbols:
            if str(symbol) not in environment['units'] and  str(symbol) not in environment['base_units']:
                continue
            
            # attempt to replace the symbol with a corresponding unit.
            try:
                units = u.find_unit(str(symbol))
                if units[0] == str(symbol):
                    sympy_expr = sympy_expr.subs({symbol: getattr(u, units[0])})
            except AttributeError:
                continue
            
        if 'base_units' in environment:
            # finally do unit conversion if needed.
            convert_units = environment['base_units']

            if len(convert_units) > 0:
                sympy_units = []
                for unit_symbol in convert_units:
                    try:
                        units = u.find_unit(str(unit_symbol))
                        sympy_units.append(getattr(u, units[0]))
                    except AttributeError:
                        continue
                    
                sympy_expr = u.convert_to(sympy_expr, sympy_units)

        return sympy_expr
