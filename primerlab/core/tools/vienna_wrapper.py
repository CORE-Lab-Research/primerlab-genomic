import subprocess
import shutil
from typing import Dict, Any, Tuple
from primerlab.core.exceptions import ToolExecutionError
from primerlab.core.logger import get_logger

logger = get_logger()

class ViennaWrapper:
    """
    Wrapper for ViennaRNA tools (RNAfold, RNAcofold).
    Gracefully handles missing installation.
    """

    _warned = False  # Class-level flag to avoid repeated warnings

    def __init__(self):
        self.rnafold_path = shutil.which("RNAfold")
        self.rnacofold_path = shutil.which("RNAcofold")

        if not self.is_available and not ViennaWrapper._warned:
            ViennaWrapper._warned = True
            logger.error(
                "❌ ViennaRNA (RNAfold/RNAcofold) not found in PATH.\n"
                "   This is a required dependency for secondary structure analysis.\n"
                "   Please install it via:\n"
                "   - Linux: sudo apt install vienna-rna\n"
                "   - Conda: conda install -c bioconda viennarna"
            )

    @property
    def is_available(self) -> bool:
        """Check if ViennaRNA tools are available."""
        return self.rnafold_path is not None

    def fold(self, sequence: str, temp: float = 37.0) -> Dict[str, Any]:
        """
        Calculates secondary structure and MFE (Minimum Free Energy) using RNAfold.
        
        Args:
            sequence: DNA/RNA sequence.
            temp: Temperature in Celsius (default 37.0).
            
        Returns:
            Dict containing 'structure', 'mfe', and 'raw_output'.
        """
        if not self.rnafold_path:
            return {"mfe": 0.0, "structure": "", "error": "RNAfold not found"}

        # RNAfold expects input via stdin
        # Parameter --noPS prevents generating postscript files
        # Parameter -T sets temperature
        # Parameter --dangles=2 is default (folding with dangling end energies)
        # Note: For DNA primers, we should ideally use DNA parameters (-P dna_mathews2004.par),
        # but standard RNAfold uses RNA parameters. For relative stability it's often acceptable,
        # or we can add a parameter to load DNA params if available.

        cmd = [self.rnafold_path, "--noPS", f"-T {temp}"]

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )
            stdout, stderr = process.communicate(input=sequence)

            if process.returncode != 0:
                raise ToolExecutionError(f"RNAfold failed: {stderr}", "ERR_TOOL_RNAFOLD")

            # Parse Output
            # Output format:
            # SEQUENCE
            # ..((...)).. (-1.50)
            lines = stdout.strip().splitlines()
            if len(lines) >= 2:
                struct_line = lines[1]
                # Extract structure and MFE
                # Example: "....(((...)))... (-1.50)"
                parts = struct_line.rsplit(" (", 1)
                structure = parts[0].strip()
                mfe_str = parts[1].replace(")", "").strip()
                mfe = float(mfe_str)

                return {
                    "structure": structure,
                    "mfe": mfe,
                    "raw": stdout
                }
            else:
                raise ToolExecutionError("Unexpected RNAfold output format", "ERR_TOOL_RNAFOLD_PARSE")

        except Exception as e:
            logger.error(f"ViennaRNA fold error: {e}")
            return {"mfe": 0.0, "structure": "", "error": str(e)}

    def cofold(self, seq1: str, seq2: str, temp: float = 37.0) -> Dict[str, Any]:
        """
        Calculates hybridization energy between two sequences using RNAcofold.
        Useful for dimer checks.
        """
        if not self.rnacofold_path:
            return {"mfe": 0.0, "structure": "", "error": "RNAcofold not found"}

        input_seq = f"{seq1}&{seq2}"
        cmd = [self.rnacofold_path, "--noPS", f"-T {temp}"]

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False
            )
            stdout, stderr = process.communicate(input=input_seq)

            if process.returncode != 0:
                raise ToolExecutionError(f"RNAcofold failed: {stderr}", "ERR_TOOL_RNACOFOLD")

            # Parse Output
            # SEQUENCE&SEQUENCE
            # ..((...))&((...)).. (-5.20)
            lines = stdout.strip().splitlines()
            if len(lines) >= 2:
                struct_line = lines[1]
                parts = struct_line.rsplit(" (", 1)
                structure = parts[0].strip()
                mfe_str = parts[1].replace(")", "").strip()
                mfe = float(mfe_str)

                return {
                    "structure": structure,
                    "mfe": mfe,
                    "raw": stdout
                }
            else:
                raise ToolExecutionError("Unexpected RNAcofold output format", "ERR_TOOL_RNACOFOLD_PARSE")

        except Exception as e:
            logger.error(f"ViennaRNA cofold error: {e}")
            return {"mfe": 0.0, "structure": "", "error": str(e)}
