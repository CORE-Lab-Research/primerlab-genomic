"""
Secondary Structure Prediction for Amplicons.

Uses ViennaRNA (RNAfold) with DNA parameters to predict
minimum free energy (MFE) secondary structure.
"""

import logging
from typing import Tuple, List, Optional

try:
    import RNA
    HAS_VIENNARNA = True
except ImportError:
    HAS_VIENNARNA = False

from .models import SecondaryStructure

logger = logging.getLogger(__name__)

# Default thresholds
DG_WARNING_THRESHOLD = -3.0  # kcal/mol
DG_ERROR_THRESHOLD = -8.0    # kcal/mol


class SecondaryStructureAnalyzer:
    """
    Predicts secondary structure of DNA amplicons using ViennaRNA.
    
    Uses DNA parameters (--dangles=2 --temp=37) for accurate modeling.
    """

    def __init__(self, config: dict = None):
        """
        Initialize analyzer.
        
        Args:
            config: Configuration dict with amplicon_analysis.secondary_structure settings
        """
        self.config = config or {}
        ss_config = self.config.get("amplicon_analysis", {}).get("secondary_structure", {})

        self.dg_warning = ss_config.get("dg_warning_threshold", DG_WARNING_THRESHOLD)
        self.dg_error = ss_config.get("dg_error_threshold", DG_ERROR_THRESHOLD)

    def predict(self, sequence: str) -> SecondaryStructure:
        """
        Predict secondary structure of amplicon using ViennaRNA.
        
        Args:
            sequence: DNA sequence (amplicon)
            
        Returns:
            SecondaryStructure with structure, delta_g, and problematic regions
        """
        seq = sequence.upper().replace("U", "T")

        if not HAS_VIENNARNA:
            logger.warning("ViennaRNA not installed. Skipping secondary structure prediction.")
            return SecondaryStructure(
                sequence=seq,
                structure="." * len(seq),
                delta_g=0.0,
                is_problematic=False,
                problematic_regions=[]
            )

        # Create fold compound with DNA parameters
        md = RNA.md()
        md.temperature = 37.0
        md.dangles = 2

        # Convert T to U for RNA folding (ViennaRNA uses RNA)
        rna_seq = seq.replace("T", "U")

        fc = RNA.fold_compound(rna_seq, md)
        structure, mfe = fc.mfe()

        # Find problematic regions (stems with low ΔG)
        problematic = self._find_problematic_regions(structure, mfe)
        is_problematic = mfe < self.dg_warning

        return SecondaryStructure(
            sequence=seq,
            structure=structure,
            delta_g=mfe,
            is_problematic=is_problematic,
            problematic_regions=problematic
        )

    def _find_problematic_regions(self, structure: str, mfe: float) -> List[Tuple[int, int]]:
        """Find stem regions in dot-bracket structure."""
        regions = []
        stack = []

        for i, char in enumerate(structure):
            if char == "(":
                stack.append(i)
            elif char == ")" and stack:
                start = stack.pop()
                # Record stems longer than 4bp
                if i - start >= 8:  # At least 4bp stem
                    regions.append((start, i))

        return regions
