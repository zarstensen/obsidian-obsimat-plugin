from ObsimatEnvironment import ObsimatEnvironment
from grammar.ObsimatLarkTransformer import ObsimatLarkTransformer
from grammar.SympyParser import SympyParser
from grammar.SubstitutionCache import SubstitutionCache

from time import sleep
from sympy import *
import sympy.parsing.latex.lark as sympy_lark
from lark import Tree, Lark
import os
from tempfile import TemporaryDirectory
import shutil


## The ObsimatLatexParser is responsible for parsing a latex string in the context of an ObsimatEnvironment.
## It also extends many functionalities of the sympy LarkLaTeXParser,
## to make it more suitable for general purpose mathematics.
class ObsimatLatexParser(SympyParser):

    def __init__(self, grammar_file: str = None):
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

            # initialize a lark parser with the same settings as LarkLaTeXParser,
            # but with propagating positions enabled.
            self.parser = Lark.open(
                os.path.join(temp_dir, "latex.lark"),
                rel_to=temp_dir,
                parser="earley",
                start="latex_string",
                lexer="auto",
                ambiguity="explicit",
                debug=True,
                propagate_positions=True,
                maybe_placeholders=False,
                keep_all_tokens=True,
            )

    # Parse the given latex expression into a sympy expression, substituting any information into the expression, present in the current environment.
    def doparse(self, latex_str: str, environment: ObsimatEnvironment = {}):
        substitution_cache = SubstitutionCache(environment, self)
        transformer = ObsimatLarkTransformer(substitution_cache)
        parse_tree = self.parser.parse(latex_str)
        expr = transformer.transform(parse_tree)
        
        # choose the highest prioritized ambiguity.
        if isinstance(expr, Tree):
            expr = expr.children[0]
        
        return expr
