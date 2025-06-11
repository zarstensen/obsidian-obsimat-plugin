import os
import re as regex
from typing import Callable, Iterator

from lark import Lark, LarkError, Token, UnexpectedInput
from lark.lark import PostLex
from lark.lexer import TerminalDef
from sympy import *

from .SympyParser import DefinitionStore, SympyParser
from .transformers.LatexTransformer import LatexTransformer


# Represents a scope to be handled by the ScopePostLexer.
# This class provides a series of terminals pairs which define the start and end of this scope.
# 
# The replace_tokens dict is a dict between a terminal type, and either:
# - A string representing the new type of this token, the value is preserved.
# - A list of TerminalDef, which (going from left to right) replaces the given terminal type, if its pattern matches its value.
class LexerScope:
    def __init__(self, 
                    scope_pairs: list[tuple[regex.Pattern, regex.Pattern|Callable[[regex.Match[str]], regex.Pattern]]] = [],
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
                    if regex.fullmatch(replace_token.pattern.to_regexp(), t.value):
                        yield Token(replace_token.name, t.value)
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
        expected_end_token_value = regex.sub(ignore_regex, '', scope_start_token.value).replace('\\begin', '\\end')
        for token in super().token_handler(token_stream, scope_start_token):
            yield token
            if token.type == expected_end_token_type and regex.sub(ignore_regex, '', token.value) == expected_end_token_value:
                yield Token('_MATRIX_ENV_END', '')

class PartialDiffScope(LexerScope):
    def token_handler(self, token_stream, _scope_start_token):
        
        for token in super().token_handler(token_stream, _scope_start_token):
            yield token
            if token.type == '_R_BRACE':
                break
        
        next_token = next(super().token_handler(token_stream, _scope_start_token))
        if next_token.type == '_L_BRACE':
            yield Token('_DERIV_ARG_SEPARATOR', next_token.value)
        else:
            yield next_token
    

# The ScopePostLexer aims to provide context to the lalr parser during tokenization.
# It does this by recognizing pairs of terminals, which define a scope.
# Inside this scope, terminals can be specified which should be replaced by other terminals,
# or optionally a custom token handler can be given, for more complex operations.
class ScopePostLexer(PostLex):
        
    # setup scopes using the terminals defined in the given parser.
    def initialize_scopes(self, parser: Lark):
        self.scopes = [
            # Scope for inner products,
            # is here so we dont go into the abs scope below.
            LexerScope(
                scope_pairs=[
                    ("_L_ANGLE", "_R_ANGLE")
                ],
                replace_tokens={
                    "_L_BAR": "_INNER_PRODUCT_SEPARATOR",
                    "_COMMA": "_INNER_PRODUCT_SEPARATOR"
                }
            ),
            # Scope for pairing up '|' characters for abs rules.
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
            # Scope for latex commands which require multiple arguments,
            # that is \command{arg1}{arg2}...{argN}.
            MultiArgScope(
                arg_count=2,
                scope_pairs=[
                    ("_FUNC_FRAC", "_MULTIARG_EOS"),
                    ("_FUNC_BINOM", "_MULTIARG_EOS")
                ]
            ),
            # Scope for functions which require the _DIFFERENTIAL_SYMBOL be prioritized over symbols.
            PartialDiffScope(
                scope_pairs=[
                    ("_FUNC_DERIVATIVE", "_R_BRACE")
                ],
                replace_tokens={
                    "SINGLE_LETTER_SYMBOL": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                    "FORMATTED_SYMBOLS": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                }
            ),
            LexerScope(
                scope_pairs=[
                    ("_FUNC_INTEGRAL", "_DIFFERENTIAL_SYMBOL"),
                    ("_DERIV_ARG_SEPARATOR", "_R_BRACE")
                ],
                replace_tokens={
                    "SINGLE_LETTER_SYMBOL": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                    "FORMATTED_SYMBOLS": [ parser.get_terminal("_DIFFERENTIAL_SYMBOL") ],
                }
            ),
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
            # General scope for L R token pairs.
            # This makes sure stuff like |(|x|)| does not get parsed as "|(|", "x" and "|)|" but instead as "|(|x|)|"
            LexerScope(
                scope_pairs=[("_?L_(.*)", lambda match : f"_?R_{match.groups()[0]}")]
            )
        ]
        
    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        yield from self._process_scope(stream, LexerScope(), None, None)
            
    def _process_scope(self, stream, scope: LexerScope, scope_begin_token: Token | None, scope_end_terminal: str | None):
        for token in scope.token_handler(stream, scope_begin_token):
            yield token
            
            # check if we are ourselves at an end terminal
            # if we are, go out of the scope.
            if scope_end_terminal is not None and regex.fullmatch(scope_end_terminal, token.type):
                break
            
            # check if the token starts a scope
            for new_scope in self.scopes:
                for scope_pair in new_scope.scope_pairs:
                    match = regex.fullmatch(scope_pair[0], token.type)
                    if match:
                        end_terminal = scope_pair[1] if isinstance(scope_pair[1], str) else scope_pair[1](match)
                        yield from self._process_scope(stream, new_scope, token, end_terminal)
                        break # do not consider other scopes
                # do not continue if the inner loop was broken out of.
                else:
                    continue
                break

## The LmatLatexParser is responsible for parsing a latex string in the context of an LmatEnvironment.
class LatexParser(SympyParser):

    def __init__(self, grammar_file: str = None):
        if grammar_file is None:
            grammar_file = os.path.join(
                os.path.dirname(__file__), "latex_math_grammar.lark"
            )
        
        post_lexer = ScopePostLexer()
        
        self.parser = Lark.open(
            grammar_file,
            rel_to=os.path.dirname(grammar_file),
            parser="lalr",
            start="latex_string",
            lexer="contextual",
            debug=False,
            cache=True,
            propagate_positions=True,
            maybe_placeholders=True,
            postlex=post_lexer
        )
        
        post_lexer.initialize_scopes(self.parser)

    # Parse the given latex expression into a sympy expression, substituting any information into the expression, present in the current environment.
    def parse(self, latex_str: str, definitions_store: DefinitionStore):        
        transformer = LatexTransformer(definitions_store)
        
        try:
            parse_tree = self.parser.parse(latex_str)
        except UnexpectedInput as e:
            raise LarkError(f"{e.get_context(latex_str, LatexParser.__PARSE_ERR_PRETTY_STR_SPAN)}{e}") from e
            
        expr = transformer.transform(parse_tree)
        
        return expr
    
    __PARSE_ERR_PRETTY_STR_SPAN = 30
