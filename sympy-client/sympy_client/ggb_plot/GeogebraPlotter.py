import os
import subprocess
import zipfile
from copy import deepcopy
from xml.etree import ElementTree

from sympy import *

from .GeogebraPrinter import print_geogebra

# Utility class for saving sympy epxressions in geogebra files, and converting these geogebra files to png plots.
class GeogebraPlotter:
    def __init__(self, ggb_install_dir, ggb_template_file):
        self._ggb_install_dir = ggb_install_dir
        self._ggb_template_file = ElementTree.parse(ggb_template_file)
        
        invalid_ggb_install_Err = RuntimeError(f'"{ggb_install_dir}" is not a valid geogebra installation directory.')
        
        try:
            result = self._run_ggb(["--v"])
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise invalid_ggb_install_Err
            
        if not result.stdout.lower().startswith(b"geogebra"):
            raise invalid_ggb_install_Err
        
    
    def sympy_to_ggb_xml(self, sympy_expr, func_args) -> ElementTree:
        # convert sympy expr to ggb expr
        ggb_expr = print_geogebra(sympy_expr)
        
        ggb_file = deepcopy(self._ggb_template_file)
        
        # Find the "construction" tag in the template file
        construction = ggb_file.getroot().find("construction")
        
        if construction is None:
            raise ValueError("The template file does not contain a 'construction' tag.")
        
        constants = sympy_expr.free_symbols - set(func_args)
        for c in constants:
            element = ElementTree.Element("element", type="numeric", label=str(c))
            ElementTree.SubElement(element, "value", val="1")
            ElementTree.SubElement(element, "labelMode", val="1")
            construction.append(element)
        
        # Add the new expression tag to the construction
        new_expression = ElementTree.Element("expression", label="f", exp=f"f({','.join((str(a) for a in func_args))}) = {ggb_expr}")
        construction.append(new_expression)
        
        
        return ggb_file
    
    def save_ggb_xml(self, ggb_xml: ElementTree, file_name: str):
        with zipfile.ZipFile(file_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr("geogebra.xml", ElementTree.tostring(ggb_xml.getroot(), encoding="utf8"))
    
    def open_ggb_file(self, file_name: str):
        return self._run_ggb([file_name])
    
    def ggb_to_png(self, file_name: str, output_name: str):
        return self._run_ggb([f"--export={output_name}.png", "--dpi=1200", file_name])
    
    def _run_ggb(self, args):
        result = subprocess.run(
            [
            f"{self._ggb_install_dir}/jre/bin/java",
            "-Xms32m",
            "-Xmx1024m",
            "-Dsun.jnu.encoding=UTF-8",
            "-jar",
            f"{self._ggb_install_dir}/geogebra.jar",
            "--logLevel=ERROR",
            "--showSplash=false",
            *args
            ],
            cwd=os.getcwd(),
            capture_output=True
        )
        
        return result
        
        
        
