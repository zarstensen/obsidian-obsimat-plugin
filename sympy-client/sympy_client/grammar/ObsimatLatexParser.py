from collections import deque
from dataclasses import dataclass
from typing import Callable, Generator, Iterator
from sympy_client.ObsimatEnvironment import ObsimatEnvironment
from .transformers.ObsimatLarkTransformer import ObsimatLarkTransformer
from .SympyParser import SympyParser
from .CachedSymbolSubstitutor import CachedSymbolSubstitutor
from .FunctionStore import FunctionStore

from sympy import *
from lark import Tree, Lark, Token
from lark.lark import PostLex
from lark.lexer import TerminalDef
import os
import re
re.Pattern
class LexerScope:
    def __init__(self, 
                    scope_pairs: list[tuple[re.Pattern, re.Pattern|Callable[[re.Match[str]], re.Pattern]]] = [],
                    replace_tokens: dict[str, str|list[TerminalDef]] = {}
                ):
        self.scope_pairs = scope_pairs
        self.replace_tokens = replace_tokens
    
    def token_handler(self, token_stream: Iterator[Token], _scope_start_token: Token) -> Iterator[Token]:
        for t in token_stream:
            # try to replace the token
            if t.type in self.replace_tokens:
                if isinstance(self.replace_tokens[t.type], str):
                    yield Token(self.replace_tokens[t.type], t.value)
                    continue
                
                for replace_token in self.replace_tokens[t.type]:
                    if re.fullmatch(replace_token.pattern.to_regexp(), t.value):
                        yield Token(str(replace_token), t.value)
                        break
                else:
                # no tokens could replace it anyways, so just return the original one.
                    yield t
            else:
                yield t

class MultiArgScope(LexerScope):
    def __init__(self, arg_count: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arg_count = arg_count
    
    def token_handler(self, token_stream: Iterator[Token], scope_start_token: Token) -> Iterator[Token]:
        for _ in range(1, self.arg_count):
            yield next(super().token_handler(token_stream, scope_start_token))
            yield Token("_MULTIARG_DELIMITER", "")
        yield next(super().token_handler(token_stream, scope_start_token))
        yield Token("_MULTIARG_EOS", "")

class MatrixScope(LexerScope):
    def token_handler(self, token_stream: Iterator[Token], scope_start_token: Token) -> Iterator[Token]:
        ignore_regex = r'(\\left\s*.|\\right\s*.|\s)'
        expected_end_token_type = scope_start_token.type.replace('BEGIN', 'END')
        expected_end_token_value = re.sub(ignore_regex, '', scope_start_token.value).replace('\\begin', '\\end')
        for token in super().token_handler(token_stream, scope_start_token):
            yield token
            if token.type == expected_end_token_type and re.sub(ignore_regex, '', token.value) == expected_end_token_value:
                yield Token('_MATRIX_ENV_END', '')
        

class ScopePostLexer(PostLex):
    def __init__(self):
        self.parser = None
    
    def initialize_scopes(self, parser: Lark):
        self.scopes = [
            LexerScope(
                scope_pairs=[
                    ("_L_ANGLE", "_R_ANGLE")
                ],
                replace_tokens={
                    "_L_BAR": "_INNER_PRODUCT_SEPARATOR",
                    "_COMMA": "_INNER_PRODUCT_SEPARATOR"
                }
            ),
            LexerScope(
                scope_pairs=[
                    ("_L_BAR", "_R_BAR"),
                    ("_L_DOUBLE_BAR", "_R_DOUBLE_BAR")
                ],
                replace_tokens={
                    "_L_BAR": "_R_BAR",
                    "_L_DOUBLE_BAR": "_R_DOUBLE_BAR",
                }
            ),
            MultiArgScope(
                arg_count=2,
                scope_pairs=[
                    ("_FUNC_FRAC", "_MULTIARG_EOS"),
                    ("_FUNC_BINOM", "_MULTIARG_EOS")
                ]
            ),
            LexerScope(
                scope_pairs=[
                    ("_FUNC_DERIVATIVE", "_R_BRACE"),
                    ("_FUNC_INT", "_DIFFERENTIAL_SYMBOL")
                ],
                replace_tokens={
                    "SINGLE_LETTER_SYMBOL": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                    "FORMATTED_SYMBOLS": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                }
            ),
            # this should have a custom token handler, which appends the end thing with MATRIX_ENV_END
            MatrixScope(
                scope_pairs=[
                    ("CMD_BEGIN_MATRIX", "_MATRIX_ENV_END"),
                    ("CMD_BEGIN_ARRAY", "_MATRIX_ENV_END"),
                    ("CMD_BEGIN_VMATRIX", "_MATRIX_ENV_END")
                ],
                replace_tokens={
                    "_ALIGN": "_MATRIX_COL_DELIM",
                    "_LATEX_NEWLINE": "MATRIX_ROW_DELIM"
                }
            ),
            LexerScope(
                scope_pairs = [
                    ("_CMD_BEGIN_ALIGN", "_CMD_END_ALIGN"),
                    ("_CMD_BEGIN_CASES", "_CMD_END_CASES")
                ],
                replace_tokens={
                    "_LATEX_NEWLINE": "_EXPR_DELIM"
                }
            ),
            LexerScope(
                scope_pairs=[("_?L_(.*)", lambda match : f"_?R_{match.groups()[0]}")]
            )
        ]
        
    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        yield from self.process_scope(stream, LexerScope(), None, None)
            
    def process_scope(self, stream, scope: LexerScope, scope_begin_token: Token | None, scope_end_terminal: str | None):
        for token in scope.token_handler(stream, scope_begin_token):
            yield token
            
            # check if we are ourselves at an end terminal
            # if we are, go out of the scope.
            if scope_end_terminal is not None and re.fullmatch(scope_end_terminal, token.type):
                break
            
            # check if the token starts a scope
            for new_scope in self.scopes:
                for scope_pair in new_scope.scope_pairs:
                    match = re.fullmatch(scope_pair[0], token.type)
                    # WE BEGINNING A NEW SCOPE BABY
                    if match:
                        end_terminal = scope_pair[1] if isinstance(scope_pair[1], str) else scope_pair[1](match)
                        yield from self.process_scope(stream, new_scope, token, end_terminal)
                        break # do not consider other scopes
                # do not continue if the inner loop was broken out of.
                else:
                    continue
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
        
        post_lexer = ScopePostLexer()
        
        self.parser = Lark.open(
            grammar_file,
            rel_to=os.path.dirname(grammar_file),
            parser="lalr",
            start="latex_string",
            lexer="contextual",
            debug=True,
            cache=True,
            propagate_positions=True,
            maybe_placeholders=True,
            postlex=post_lexer
        )
        
        post_lexer.initialize_scopes(self.parser)

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