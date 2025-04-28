from sympy_client.ggb_plot.GeogebraPrinter import print_geogebra
from sympy import *

class TestGeogebraPrinter:
    def test_equalities(self):
        x, y = symbols("x y")
        assert print_geogebra(Eq(2 * x, 3 * y)).replace(" ", "") == "(2*x)=(3*y)"
        
    def test_matrices(self):
        x, y, z, u, t = symbols("x y z u t")
        
        assert print_geogebra(Matrix([x, y, z])).replace(" ", "") == "(x,y,z)"
        assert print_geogebra(Matrix([cos(u), sin(u), t]).T).replace(" ", "") == "(cos(u),sin(u),t)"
        
        assert print_geogebra(Matrix([
            [x,      2,   3     ],
            [y + z,  x**2,6     ],
            [sqrt(y),8,   log(x)]
            ])).replace(" ", "") == "{{x,2,3},{y+z,x**2,6},{sqrt(y),8,log(x)}}"
        
    def test_functions(self):
        x = symbols("x")
        assert print_geogebra(abs(x)).replace(" ", "") == "abs(x)"
