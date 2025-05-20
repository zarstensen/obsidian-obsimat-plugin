from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from .ObsimatLarkTransformer import ObsimatLarkTransformer
from .SympyParser import SympyParser
from .CachedSymbolSubstitutor import CachedSymbolSubstitutor
from .FunctionStore import FunctionStore

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
                os.path.dirname(__file__), "obsimat_larl_grammar.lark"
            )

        # initialize a lark parser with the same settings as LarkLaTeXParser,
        # but with propagating positions enabled.
        
        self.parser = Lark.open(
            grammar_file,
            rel_to=os.path.dirname(grammar_file),
            parser="lalr",
            start="latex_string",
            lexer="auto",
            debug=True,
            propagate_positions=True,
            maybe_placeholders=False,
            keep_all_tokens=True,
        )

    # Parse the given latex expression into a sympy expression, substituting any information into the expression, present in the current environment.
    def doparse(self, latex_str: str, environment: ObsimatEnvironment = {}):
        symbol_substitutor = CachedSymbolSubstitutor(environment, self)
        function_store = FunctionStore(environment, self)
        
        transformer = ObsimatLarkTransformer(symbol_substitutor, function_store)
        parse_tree = self.parser.parse(latex_str)
        expr = transformer.transform(parse_tree)
        
        # choose the highest prioritized ambiguity.
        if isinstance(expr, Tree):
            expr = expr.children[0]
        
        return expr