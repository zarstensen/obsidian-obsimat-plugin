import sympy.physics.units as u
from sympy import *
from sympy_client.ObsimatPrinter import ObsimatPrinter


class TestObsimatPrinter:
    printer = ObsimatPrinter()
    
    def test_numeric_fraction(self):
        latex_str = self.printer.doprint(Rational(1, 2))
        self._assert_str_equal(r'\frac{1}{2}', latex_str)
    
    def test_fraction_with_symbols(self):
        a, b = symbols("a b")
        latex_str = self.printer.doprint((5 * a) / (2 * b))
        self._assert_str_equal(r'\frac{5}{2} \, \frac{a}{b}',latex_str)
    
    def test_fraction_with_units(self):
        latex_str = self.printer.doprint((5 * u.km) / (u.hour))
        self._assert_str_equal(r'5 \, \frac{{km}}{{hour}}',latex_str)
    
    def test_fraction_with_symbols_and_units(self):
        a, b = symbols("a b")
        latex_str = self.printer.doprint((7 * a**2 * u.joule) / (3 * b * u.second**2))
        # TODO: this string is not parsable by the new parser, {s}^{2} is not recognized.
        # also the output should probably be {{s}}^2
        self._assert_str_equal(r'\frac{7}{3} \, \frac{a^{2}}{b} \, \frac{{J}}{{s}^{2}}',latex_str)
    
    def test_not_to_be_formatted_fraction(self):
        a, b = symbols("a b")
        latex_str = self.printer.doprint((a + b**2) / (27 - b))
        self._assert_str_equal(r'\frac{a + b^{2}}{27 - b}', latex_str)
    
    def _assert_str_equal(self, expected, actual):
        assert ''.join(expected.split()) == ''.join(actual.split())
        