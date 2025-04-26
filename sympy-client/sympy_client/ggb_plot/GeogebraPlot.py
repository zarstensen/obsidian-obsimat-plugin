import os
import subprocess
from typing import Iterable
import zipfile
from copy import deepcopy
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from sympy_client.grammar.CachedSymbolSubstitutor import CachedSymbolSubstitutor
from sympy_client.grammar.FunctionStore import FunctionStore

from sympy import *
from sympy.core.relational import Relational

from .GeogebraPrinter import print_geogebra

# Utility class for saving sympy epxressions in geogebra files, and converting these geogebra files to png plots.
# TODO: this should work with the portable version (which persumably is the excact same as the installed version, only it is in the plugin dir)
# nah macos is wierd try to look for a portable version maybe but it does not really matter.
# also it increases the size of the plugin a lot so probably not worth it.
class GeogebraPlot:
    
    AXIS_SYMBOLS = symbols('x y z')
    
    def __init__(self, ggb_template_file, function_store: FunctionStore):
        self._function_store = function_store
        # ONLY very fy this the first time _run_ggb is called.
        self._ggb_template_file = ElementTree.parse(ggb_template_file)
        self._construction = self._ggb_template_file.getroot().find('construction')
        self._defined_constants = set(GeogebraPlot.AXIS_SYMBOLS)
        self._has_contour_plot = False
    
    def plot_function(self, name: str, args: Iterable[Symbol], expr: Expr, visible: bool = True) -> tuple[Element, tuple[Element]]:
        constants = self._define_constants(expr.free_symbols - set(args))
        
        expression_element = ElementTree.SubElement(self._construction, 'expression', label=name, exp=f"{name}({','.join((str(a) for a in args))}) = {print_geogebra(expr)}")
        
        if not visible:
            ElementTree.SubElement(
                self._construction, 'element', type='function', label=name
            ).extend([
                Element('show', object="false")
            ])
        
        return (expression_element, constants)
    
    def plot_relation(self, sympy_relation: Relational) -> Element:
        # this is a blessing in disguise, because relations should be different.
        # each expression has to be a function apparently.
        # also define the functions here if they are in the function_store i think?

        lhs = sympy_relation.lhs
        rhs = sympy_relation.rhs
        
        sympy_relation = type(sympy_relation)(self._try_replace_func(lhs), self._try_replace_func(rhs))

        expression_element = Element("expression", exp=print_geogebra(sympy_relation))
        self._construction.append(expression_element)
        
        return expression_element
    
    def plot_contour_curves(self, expr: Expr):
        
        # only 1 conour plot pr. plot is allowed.
        assert not self._has_contour_plot
        
        self._has_contour_plot
        
        ElementTree.SubElement(
            self._construction, "element",type='numeric',label='C_r_a_n_g_e'
        ).extend([
            Element('value', val="100.0"),        
        ])
        
        ElementTree.SubElement(
            self._construction, "element", type='numeric',label='N'
        ).extend([
            Element('value', val="3"),
            Element('show', object="true", label="true"),
            Element('slider', min='0', max='25', absoluteScreenLocation="true"),
            Element('animation', step="1"),      
            Element('labelMode', val="1") 
        ])
        
        ElementTree.SubElement(
            self._construction, "element", type='numeric',label='C_m_i_n'
        ).extend([
            Element('value', val="-100.0"),
            Element('show', object="true", label="true"),
            Element('slider', min='-C_r_a_n_g_e', max='C_r_a_n_g_e', absoluteScreenLocation="true"),
            Element('animation', step="0.1"),
            Element('labelMode', val="1") 
        ])
        
        ElementTree.SubElement(
            self._construction, "element", type='numeric',label='C_m_a_x'
        ).extend([
            Element('value', val="100.0"),
            Element('show', object="true", label="true"),
            Element('slider', min='-C_r_a_n_g_e', max='C_r_a_n_g_e', absoluteScreenLocation="true"),
            Element('animation', step="0.1"),      
            Element('labelMode', val="1") 
        ])
        
        ElementTree.SubElement(
            self._construction, "expression", label='CenterPoint', exp='Corner[4] - (Corner[4] - Corner[2]) / 2', type='point'
        )
        
        ElementTree.SubElement(
            self._construction, "element", type='point', label='CenterPoint'
        ).extend([
            Element('show', object="false")
        ])
        
        
        
        # ANOTHEr sequence should be here which is the level set values, which are used in the labeling.
        
        ElementTree.SubElement(
            self._construction, 'command', name='Sequence'
        ).extend([
            Element('input', a0=f'c', a1='c', a2='C_m_i_n', a3='C_m_a_x', a4='abs(C_m_i_n - C_m_a_x) / N'),
            Element('output', a0='LevelSets')
        ])
        
        # Create sequence for contour curves
        ElementTree.SubElement(
            self._construction, "command", name="Zip"
        ).extend([
            Element("input", a0=f'c = {print_geogebra(self._try_replace_func(expr))}', a1="c", a2="LevelSets"),
            Element("output", a0="ContourCurves")
        ])
        
        # Create sequence for contour labels
        ElementTree.SubElement(
            self._construction, "command", name="Zip"
        ).extend([
            Element("input", a0=f'Text[c, ClosestPoint[CC, CenterPoint]]', a1="CC", a2="ContourCurves", a3="c", a4="LevelSets"),
            Element("output", a0="ContourLabels")
        ])
        
        pass
    
    def plot_vector_field(self, expr):
        pass
    
    def save_to_ggb(self, out_file: str):
        with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("geogebra.xml", ElementTree.tostring(self._ggb_template_file.getroot(), encoding="utf8"))
    
    # If the given expression is in the FunctionStore,
    # define the function in the geogebra plot, and return an expression
    # which calls the method with up to 3 variables (x, y, z).
    def _try_replace_func(self, expr: Expr) -> Expr:
        if expr not in self._function_store:
            return expr
        
        func = self._function_store[expr]
        self.plot_function(str(expr), func.args, func.parse_body(), visible=False)
        
        return Function(str(expr))(*GeogebraPlot.AXIS_SYMBOLS[:len(func.args)])
            
    def _define_constants(self, constants: set[Symbol]) -> tuple[Element]:
        
        added_constants = []
        
        for c in filter(lambda c: str(c) not in self._defined_constants, constants):
            self._defined_constants.add(str(c))
            
            constant_element = Element("element", type="numeric", label=str(c))
            ElementTree.SubElement(constant_element, "value", val="1")
            ElementTree.SubElement(constant_element, "labelMode", val="1")
            
            added_constants.append(constant_element)
        
        self._construction.extend(added_constants)
        
        return tuple(added_constants)

    
    # def sympy_to_ggb_xml(self, sympy_expr, func_args) -> ElementTree:
    #     # x y z can never be defined as constants due to geogebra stuff.
    #     func_args = set(func_args).union(symbols('x y z'))
        
    #     # convert sympy expr to ggb expr
    #     ggb_expr = print_geogebra(sympy_expr)
        
    #     ggb_file = deepcopy(self._ggb_template_file)
        
    #     # Find the "construction" tag in the template file
    #     construction = ggb_file.getroot().find("construction")
        
    #     if construction is None:
    #         raise ValueError("The template file does not contain a 'construction' tag.")
        
    #     constants = sympy_expr.free_symbols - set(func_args)
    #     for c in constants:
    #         element = ElementTree.Element("element", type="numeric", label=str(c))
    #         ElementTree.SubElement(element, "value", val="1")
    #         ElementTree.SubElement(element, "labelMode", val="1")
    #         construction.append(element)
        
    #     # Add the new expression tag to the construction
    #     new_expression = ElementTree.Element("expression", label="f", exp=f"f({','.join((str(a) for a in func_args))}) = {ggb_expr}")
    #     construction.append(new_expression)
        
        
    #     return ggb_file
    
    # def save_ggb_xml(self, ggb_xml: ElementTree, file_name: str):
    #     with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
    #         zipf.writestr("geogebra.xml", ElementTree.tostring(ggb_xml.getroot(), encoding="utf8"))
        
