from enum import Enum
from typing import TypedDict, override

from sympy import *
from sympy.logic.boolalg import Boolean, as_Boolean, truth_table
from tabulate import tabulate

from sympy_client.grammar.LmatEnvDefStore import LmatEnvDefStore
from sympy_client.grammar.SympyParser import SympyParser
from sympy_client.grammar.transformers.PropositionsTransformer import PropositionExpr
from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.LmatLatexPrinter import lmat_latex

from .CommandHandler import *


class TruthTableFormat(Enum):
    MARKDOWN = "md"
    LATEX_ARRAY = "latex-array"

class TruthTableMessage(TypedDict):
    expression: str
    environment: LmatEnvironment
    table_format: TruthTableFormat

class TruthTableResult(CommandResult):
    def __init__(self, columns: tuple[Expr], serialized_proposition: str, truth_table: tuple[tuple[Boolean]]):
        super().__init__()
        self.columns = columns
        self.serialized_proposition = serialized_proposition
        self.truth_table = truth_table

class TruthTableResultMarkdown(TruthTableResult):

    def getPayload(self) -> dict:
        markdown_table_contents = []

        for row in self.truth_table:
            markdown_table_contents.append([ "T" if elem else "F" for elem in row ])
            markdown_table_contents[-1][-1] = f"**{markdown_table_contents[-1][-1]}**"

        headers = [*map(lmat_latex, self.columns), self.serialized_proposition]
        headers = [ f"${header}$" for header in headers ]

        return CommandResult.result({
            'truth_table': tabulate(markdown_table_contents,
                                    headers=headers,
                                    tablefmt='pipe',
                                    colalign=('center' for _ in range(len(self.columns) + 1)))
        })

class TruthTableResultLatex(TruthTableResult):

    def getPayload(self) -> dict:
        markdown_table_contents = []

        for row in self.truth_table:
            markdown_table_contents.append("&".join(map(lmat_latex, row)))

        return CommandResult.result({
            'truth_table': fr"\begin{{array}}{{{':'.join(('c' for _ in self.columns))}|c}}{'&'.join(map(lmat_latex, self.columns))} & {self.serialized_proposition}\\ \hline{r'\\ \hline '.join(markdown_table_contents)}\end{{array}}"
        })

# Inherit from EvalHandlerBase, override its thing so the result is taken from its result,
# evaluate should do nothing, not even simplify.
# then use dependency injection for the result objects.
class TruthTableHandler(CommandHandler):

    def __init__(self, parser: SympyParser):
        super().__init__()
        self._parser = parser

    @override
    def handle(self, message: TruthTableMessage) -> TruthTableResult | ErrorResult:
        definitions_store = LmatEnvDefStore(self._parser, message['environment'])
        sympy_expr = self._parser.parse(message['expression'], definitions_store)

        if not isinstance(sympy_expr, PropositionExpr):
            return ErrorResult(f"Expression must be a proposition, was {type(sympy_expr)}")

        sympy_expr = sympy_expr.expr

        columns = sorted(sympy_expr.free_symbols, key=str)

        truth_table_data = []

        for row in reversed(tuple(truth_table(sympy_expr, columns))):
            truth_table_data.append([*map(as_Boolean, row[0]), row[1]])

        result_cls = None

        match message['table_format']:
            case TruthTableFormat.MARKDOWN.value:
                result_cls = TruthTableResultMarkdown
            case TruthTableFormat.LATEX_ARRAY.value:
                result_cls = TruthTableResultLatex
            case _:
                return ErrorResult(f"Unknown table format: {message['table_format']}")

        return result_cls(columns, message['expression'], truth_table_data)
