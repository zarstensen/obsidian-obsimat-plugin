from sympy import *
import sympy.physics.units as u
from sympy.parsing.latex import parse_latex_lark
from lark import Tree
from ObsimatEnvironment import ObsimatEnvironment
import regex

class LatexParser:
    
    @staticmethod
    def parse_latex(latex_str: str, environment: ObsimatEnvironment):
        # Substitute variables with regex here, instead of using sympys builtin substitution,
        # As sympy sometimes make some "incorrect" assumptions about variables,
        # which leads to substitution failure.
        latex_str = LatexParser.__VARIABLE_REGEX.sub(
            lambda m: LatexParser.__variable_substituter(m, environment),
            latex_str
            )
        
        # Surround all detected multi-letter variables with \mathit{} so sympy knows to treat them as single variables.
        latex_str = LatexParser.__MULTI_LETTER_VARIABLE_REGEX.sub(LatexParser.__multi_letter_variable_substituter, latex_str)
        
        # Finally, remove any escaped spaces as sympy cannot figure out how to parse this
        latex_str = latex_str.replace(r"\ ", " ")
        
        print(latex_str, flush=True)
        
        sympy_expr = parse_latex_lark(latex_str)

        if type(sympy_expr) is Tree:
            sympy_expr = sympy_expr.children[0]
        
        with evaluate(False):
            # now, replace all the symbols with the ones defined in the passed environment.
            for symbol in sympy_expr.free_symbols:
                if str(symbol) in environment['symbols']:
                    assumptions = {}
                    for assumption in environment['symbols'][str(symbol)]:
                        assumptions[assumption] = True
                    
                    # TODO: warn here if an assumption is not recognized.
                    # create the sympy symbol here
                    sympy_symbol = Symbol(str(symbol), **assumptions)
                    
                    # and substitute the new symbol here.
                    sympy_expr = sympy_expr.subs({symbol: sympy_symbol})

        return sympy_expr
    
    @staticmethod
    def handle_units(sympy_expr, environment: ObsimatEnvironment):
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
    
    # TODO: comments here
    @staticmethod
    def __variable_substituter(match: regex.Match[str], environment: ObsimatEnvironment) -> str:
        if match.groupdict()['variable_name'] in environment['variables']:
            return f"({environment['variables'][match.groupdict()['variable_name']]})"
        else:
            return match.groupdict()['original']
        
    @staticmethod
    def __multi_letter_variable_substituter(match: regex.Match[str]) -> str:
        print(match.regs, flush=True)
        print(match.allspans(), flush=True)
        spans = match.regs
        match_span = spans[0]
        variable_span = spans[LatexParser.__MULTI_LETTER_VARIABLE_REGEX.groupindex['multiletter_variable']]
        print(spans, flush=True)
        print(match.string, flush=True)
        return f"\\mathit{{{match.groupdict()['multiletter_variable']}}}".join((match.string[match_span[0]:variable_span[0]], match.string[variable_span[1]:match_span[1]]))
    
    __VARIABLE_REGEX = regex.compile(r'(?P<original>(?:\\math[a-zA-Z]*{)(?P<variable_name>(?R)*)}|(?P<variable_name>\\?[a-zA-Z][a-zA-Z0-9]*(?:_{(?>.|(?R))*?}|_.)?))')
    __MULTI_LETTER_VARIABLE_REGEX = regex.compile(r'(?<!\\end)(?<!\\begin)(?:[^\w\\]|^){1,}?(?P<multiletter_variable>[a-zA-Z]{2,})(?=[^\w]|$)')
    
