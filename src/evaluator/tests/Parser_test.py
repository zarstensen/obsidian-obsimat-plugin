from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils

from sympy import *

class TestParse:
    def test_mathematical_constants(self):
        result = ObsimatEnvironmentUtils.parse_latex(r"\pi", {})

        assert result == S.Pi
    