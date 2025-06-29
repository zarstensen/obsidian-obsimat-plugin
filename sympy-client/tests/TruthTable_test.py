from sympy import *
from sympy_client.command_handlers.TruthTableHandler import (
    TruthTableHandler,
)
from sympy_client.grammar.LatexParser import LatexParser


class TestTruthTable:
    handler = TruthTableHandler(LatexParser())

    def test_truth_table(self):
        p, q, r = symbols('P Q R')

        result = self.handler.handle({ 'expression': r"P \wedge Q",
                             'environment': {},
                             'table_format': "md"
                             })

        assert result.columns == [p, q]
        assert result.truth_table == [
            [True,  True,  True],
            [True,  False, False],
            [False, True,  False],
            [False, False, False],
        ]
