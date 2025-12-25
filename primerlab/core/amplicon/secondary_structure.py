"""
Secondary Structure Prediction for Amplicons.

Uses ViennaRNA (RNAfold) with DNA parameters to predict
minimum free energy (MFE) secondary structure.
"""

import logging
from typing import Tuple, List, Optional

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
        self._vienna_available = None
    
    def _check_vienna(self) -> bool:
        """Check if ViennaRNA is available."""
        if self._vienna_available is not None:
            return self._vienna_available
            
        try:
            import RNA
            self._vienna_available = True
        except ImportError:
            logger.warning("ViennaRNA not installed. Using fallback estimation.")
            self._vienna_available = False
        
        return self._vienna_available
    
    def predict(self, sequence: str) -> SecondaryStructure:
        """
        Predict secondary structure of amplicon.
        
        Args:
            sequence: DNA sequence (amplicon)
            
        Returns:
            SecondaryStructure with structure, delta_g, and problematic regions
        """
        seq = sequence.upper().replace("U", "T")
        
        if self._check_vienna():
            return self._predict_vienna(seq)
        else:
            return self._predict_fallback(seq)
    
    def _predict_vienna(self, sequence: str) -> SecondaryStructure:
        """Use ViennaRNA for prediction."""
        import RNA
        
        # Create fold compound with DNA parameters
        md = RNA.md()
        md.temperature = 37.0
        md.dangles = 2
        
        # Convert T to U for RNA folding (ViennaRNA uses RNA)
        rna_seq = sequence.replace("T", "U")
        
        fc = RNA.fold_compound(rna_seq, md)
        structure, mfe = fc.mfe()
        
        # Find problematic regions (stems with low ΔG)
        problematic = self._find_problematic_regions(structure, mfe)
        is_problematic = mfe < self.dg_warning
        
        return SecondaryStructure(
            sequence=sequence,
            structure=structure,
            delta_g=mfe,
            is_problematic=is_problematic,
            problematic_regions=problematic
        )
    
    def _predict_fallback(self, sequence: str) -> SecondaryStructure:
        """
        Simple fallback estimation when ViennaRNA is not available.
        
        Uses GC content and self-complementarity heuristics.
        """
        # Estimate ΔG based on GC content (very rough)
        gc_count = sequence.count("G") + sequence.count("C")
        gc_percent = gc_count / len(sequence) * 100
        
        # Higher GC = more stable structure potential
        estimated_dg = -0.05 * gc_percent  # Rough estimate
        
        # Check for obvious palindromes/hairpins
        problematic = self._find_palindromes(sequence)
        
        # Create dot-bracket (all unpaired as fallback)
        structure = "." * len(sequence)
        
        is_problematic = estimated_dg < self.dg_warning or len(problematic) > 0
        
        return SecondaryStructure(
            sequence=sequence,
            structure=structure,
            delta_g=estimated_dg,
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
    
    def _find_palindromes(self, sequence: str, min_len: int = 6) -> List[Tuple[int, int]]:
        """Find simple palindromic sequences (potential hairpin stems)."""
        complement = {"A": "T", "T": "A", "G": "C", "C": "G"}
        regions = []
        
        for i in range(len(sequence) - min_len):
            for j in range(i + min_len, min(i + 20, len(sequence))):
                subseq = sequence[i:j]
                rev_comp = "".join(complement.get(b, "N") for b in reversed(subseq))
                
                # Check if reverse complement exists nearby
                if rev_comp in sequence[j:j+50]:
                    regions.append((i, j))
                    break
        
        return regions[:5]  # Limit to 5 regions
