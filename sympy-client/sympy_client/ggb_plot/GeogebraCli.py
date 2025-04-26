import os
import subprocess


class GeogebraCli:
    def __init__(self, ggb_install_dir):
        self._ggb_install_dir = ggb_install_dir

        invalid_ggb_install_Err = RuntimeError(f'"{ggb_install_dir}" is not a valid geogebra installation directory.')
        
        try:
            result = self._run_ggb(["--v"])
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            raise invalid_ggb_install_Err
            
        if not result.stdout.lower().startswith(b"geogebra"):
            raise invalid_ggb_install_Err
        
    def open_ggb_file(self, file_name: str):
        return self._run_ggb([file_name])
    
    def export_ggb_file(self, file_name: str, output_name: str, dpi: int = 600):
        return self._run_ggb([f"--export={output_name}", f"--dpi={dpi}", file_name])
        
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