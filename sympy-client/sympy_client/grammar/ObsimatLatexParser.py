from collections import deque
from typing import Iterator
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from .transformers.ObsimatLarkTransformer import ObsimatLarkTransformer
from .SympyParser import SympyParser
from .CachedSymbolSubstitutor import CachedSymbolSubstitutor
from .FunctionStore import FunctionStore

from sympy import *
import sympy.parsing.latex.lark as sympy_lark
from lark import Tree, Lark, Token
from lark.lark import PostLex
import os
from tempfile import TemporaryDirectory
import shutil
import re

class MultiargFuncDelimiter(PostLex):
    FUNC_PREFIX = 'MULTIARG_FUNC_'
    
    L_ARG_BRACES = 'L_BRACE'
    R_ARG_BRACES = 'R_BRACE'
    
    ARG_DELIMITER = 'MULTIARG_FUNC_ARG_DELIMITER'
    
    SAME_LR_DELIMS = { 'BAR', 'DOUBLE_BAR' }
    LR_DELIMS_IGNORE = {
        'ANGLE': {'BAR'} # ignore bar, if inside ANGLE scope currently.
    }
    
    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        yield from self._handle_delim(stream)

    # TODO: make this recursive, it should consider ALL LR delims, and if it encounters
    def _handle_delim(self, stream: Iterator[Token], curr_delim: str = None) -> Iterator[Token]:
        for token in stream:
            yield token
            token_type = token.type
            
            # need to check if this is a same delim, or just a standard delim.
            if token_type.startswith('L_'):
                delim_type = token_type[2:]
                
                
                if delim_type in self.SAME_LR_DELIMS:
                    
                    if delim_type in self.LR_DELIMS_IGNORE.get(delim_type, {}):
                        continue
                    
                    yield from self._handle_same_delim(stream, delim_type)
                else:
                    yield from self._handle_delim(stream, delim_type)
                
            # ok we have hit the end of this scope, go up one level.
            elif token_type.startswith('R_') and token_type[2:] == curr_delim:
                break
                
    def _handle_same_delim(self, stream: Iterator[Token], curr_delim: str) -> Iterator[Token]:
        for token in stream:
            token_type: str = token.type
            
            if token_type.startswith('L_'):
                delim_type = token_type[2:]
                if delim_type in self.SAME_LR_DELIMS:
                    # check if it is already in the stack, if so convert it to an R_ version.
                    if curr_delim == delim_type:
                        yield Token(f"R_{delim_type}", token.value)
                        break
                    else:
                        yield token
                        yield from self._handle_same_delim(stream, delim_type)
                else:
                    yield token
                    yield from self._handle_delim(stream, delim_type)
            elif token_type == curr_delim:
                yield Token(f"R_{curr_delim}", token.value)
                break
            else:
                yield token

    def _handle_multiarg(self, stream):
        for token in stream:
            # time for special handling
            if token.type.startswith(self.FUNC_PREFIX):
                yield token
                yield from self._handle_multiarg_func(token, stream)    
            else:
                yield token

    def _handle_multiarg_func(self, func_token, stream):
        # we are now inside a special multiarg function call, time to get how may arguments there are
        match = re.match(f'{self.FUNC_PREFIX}(\\d+).*', func_token.type)
        arg_count = int(match.group(1)) if match else None
        
        delim_token = Token(self.ARG_DELIMITER, '')
        
        for token in stream:
            yield token

            if arg_count <= 1:
                break
            
            if token.type == self.L_ARG_BRACES:
                yield from self._handle_brace_surrounded_arg(stream)    

            yield delim_token
            
            arg_count -= 1

    def _handle_brace_surrounded_arg(self, stream):
        depth = 1
        
        for token in stream:
            yield token
            
            if token.type == self.L_ARG_BRACES:
                depth += 1
            elif token.type == self.R_ARG_BRACES:
                depth -= 1
            
            if depth <= 0:
                break
            

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
            start="expression",
            lexer="contextual",
            debug=True,
            cache=True,
            propagate_positions=True,
            maybe_placeholders=False,
            keep_all_tokens=True,
            postlex=MultiargFuncDelimiter()
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