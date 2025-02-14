from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
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


## The ObsimatLatexParser is responsible for parsing a latex string in the context of an ObsimatEnvironment.
## It also extends many functionalities of the sympy LarkLaTeXParser,
## to make it more suitable for general purpose mathematics.
class ObsimatLatexParser(LarkLaTeXParser):

    def __init__(self, print_debug_output: bool = False, grammar_file: str = None):
        self.__environment = {}

        # append the given grammar file to the end of sympys grammar file,
        # and give it to the super constructor.
        # that way we can extend sympys grammar with our own rules and terminals.
        if grammar_file is None:
            grammar_file = os.path.join(
                os.path.dirname(__file__), "obsimat_grammar.lark"
            )

        with TemporaryDirectory() as temp_dir:
            for file in os.listdir(
                os.path.join(os.path.dirname(sympy_lark.__file__), "grammar")
            ):
                if file.endswith(".lark"):
                    shutil.copy(
                        os.path.join(
                            os.path.dirname(sympy_lark.__file__), "grammar", file
                        ),
                        temp_dir,
                    )

            with open(os.path.join(temp_dir, "latex.lark"), "a") as f:
                with open(grammar_file, "r") as custom_grammar:
                    f.write("\n" + custom_grammar.read())

            # since we want to construct the transformer ourselves, we pass this lambda constructor instead of just the type.
            super().__init__(
                print_debug_output=print_debug_output,
                transform=True,
                transformer=lambda: ObsimatLarkTransformer(self),
                grammar_file=os.path.join(temp_dir, "latex.lark"),
            )
    # Set the ObsimatEnvironment this parser should use when executing doparse.
    def set_environment(self, environment: ObsimatEnvironment):
        self.__environment = environment

    def get_environment(self) -> ObsimatEnvironment:
        return self.__environment

    # Parse the given latex expression into a sympy expression, substituting any information into the expression, present in the current environment.
    def doparse(self, latex_str: str):
        latex_str = self.__substitute_variables(latex_str)

        # Surround all detected multi-letter variables with \mathit{} so sympy knows to treat them as single variables.
        latex_str = ObsimatLatexParser.__MULTI_LETTER_VARIABLE_REGEX.sub(
            ObsimatLatexParser.__multi_letter_variable_substituter, latex_str
        )

        sympy_expr = super().doparse(latex_str)

        if isinstance(sympy_expr, Tree):
            sympy_expr = sympy_expr.children[0]
        elif isinstance(sympy_expr, list):
            sympy_expr = [self.__substitute_symbols(expr) for expr in sympy_expr]
        elif isinstance(sympy_expr, Expr):
            sympy_expr = self.__substitute_symbols(sympy_expr)

        return sympy_expr

    def __substitute_variables(self, latex_str: str):
        if "variables" not in self.get_environment():
            return latex_str

        # Substitute variables with regex here, instead of using sympys builtin substitution,
        # As sympy sometimes make some "incorrect" assumptions about variables,
        # which leads to substitution failure.

        for _ in range(ObsimatLatexParser.__MAX_SUBSTITUTION_DEPTH):
            prev_str = latex_str
            latex_str = ObsimatLatexParser.__VARIABLE_REGEX.sub(
                lambda m: self.__variable_substituter(m), latex_str
            )

            if prev_str == latex_str:
                break

        else:
            raise RecursionError(
                f"Max substitution depth reached. ({ObsimatLatexParser.__MAX_SUBSTITUTION_DEPTH})"
            )

        return latex_str

    def __substitute_symbols(self, sympy_expr: Any):
        if "symbols" not in self.get_environment():
            return sympy_expr

        with evaluate(False):

            # now, replace all the symbols with the ones defined in the passed environment.
            for symbol in sympy_expr.free_symbols:
                if str(symbol) in self.get_environment()["symbols"]:
                    # and substitute the new symbol here.
                    sympy_expr = sympy_expr.subs(
                        {
                            symbol: ObsimatEnvironmentUtils.create_sympy_symbol(
                                symbol, self.get_environment()
                            )
                        }
                    )

        return sympy_expr

    __MAX_SUBSTITUTION_DEPTH = 100

    __VARIABLE_REGEX = regex.compile(
        r"(?P<original>(?:\\math[a-zA-Z]*{)(?P<variable_name>(?R)*)}|(?P<variable_name>\\?[a-zA-Z][a-zA-Z0-9]*(?:_{(?>.|(?R))*?}|_.)?))"
    )
    __MULTI_LETTER_VARIABLE_REGEX = regex.compile(
        r"(?<!\\end)(?<!\\begin)(?:[^\w\\]|^){1,}?(?P<multiletter_variable>[a-zA-Z]{2,})(?=[^\w]|$)"
    )

    # TODO: comments here
    def __variable_substituter(self, match: regex.Match[str]) -> str:
        if match.groupdict()["variable_name"] in self.get_environment()["variables"]:
            return f"({self.get_environment()['variables'][match.groupdict()['variable_name']]})"
        else:
            return match.groupdict()["original"]

    @staticmethod
    def __multi_letter_variable_substituter(match: regex.Match[str]) -> str:
        spans = match.regs
        match_span = spans[0]
        variable_span = spans[
            ObsimatLatexParser.__MULTI_LETTER_VARIABLE_REGEX.groupindex[
                "multiletter_variable"
            ]
        ]
        return f"\\mathit{{{match.groupdict()['multiletter_variable']}}}".join(
            (
                match.string[match_span[0] : variable_span[0]],
                match.string[variable_span[1] : match_span[1]],
            )
        )
