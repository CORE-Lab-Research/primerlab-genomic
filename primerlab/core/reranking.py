"""
Multi-Candidate Re-ranking Engine for v0.1.3

This module evaluates multiple primer candidates from Primer3,
applies ViennaRNA QC thresholds, and selects the best candidate.
"""

import random
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from primerlab.core.models import Primer
from primerlab.core.tools.vienna_wrapper import ViennaWrapper
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class CandidateScore:
    """Holds scoring data for a primer candidate."""
    index: int
    primer3_penalty: float
    hairpin_dg: float
    homodimer_dg: float
    passes_qc: bool
    rejection_reason: Optional[str] = None


class RerankingEngine:
    """
    Evaluates multiple primer candidates and selects the best one
    based on ViennaRNA thermodynamic analysis.
    """
    
    # Default QC thresholds
    DEFAULT_THRESHOLDS = {
        "strict": {"hairpin_dg_max": -6.0, "homodimer_dg_max": -6.0, "heterodimer_dg_max": -6.0},
        "standard": {"hairpin_dg_max": -9.0, "homodimer_dg_max": -9.0, "heterodimer_dg_max": -9.0},
        "relaxed": {"hairpin_dg_max": -12.0, "homodimer_dg_max": -12.0, "heterodimer_dg_max": -12.0}
    }
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the re-ranking engine with QC thresholds.
        
        Args:
            config: Full workflow configuration dict
        """
        self.vienna = ViennaWrapper()
        
        params = config.get("parameters", {})
        qc_config = config.get("qc", {})
        advanced = config.get("advanced", {})
        
        # Get QC mode preset or individual thresholds
        qc_mode = qc_config.get("mode", "standard")
        preset = self.DEFAULT_THRESHOLDS.get(qc_mode, self.DEFAULT_THRESHOLDS["standard"])
        
        self.hairpin_dg_max = qc_config.get("hairpin_dg_max", preset["hairpin_dg_max"])
        self.homodimer_dg_max = qc_config.get("homodimer_dg_max", preset["homodimer_dg_max"])
        self.heterodimer_dg_max = qc_config.get("heterodimer_dg_max", preset["heterodimer_dg_max"])
        
        self.show_alternatives = params.get("show_alternatives", 5)
        
        # v0.1.3: Seed for reproducible selection
        self.seed = advanced.get("seed", None)
        if self.seed is not None:
            random.seed(self.seed)
            logger.info(f"Reproducibility seed set: {self.seed}")
        
        logger.info(f"Re-ranking Engine initialized with QC mode: {qc_mode}")
    
    def evaluate_candidate(self, fwd_seq: str, rev_seq: str, primer3_penalty: float = 0.0) -> Tuple[bool, Dict[str, Any]]:
        """
        Evaluate a single primer pair candidate.
        
        Returns:
            Tuple of (passes_qc, details_dict)
        """
        from primerlab.core.sequence_qc import check_gc_clamp, check_poly_x
        
        details = {
            "primer3_penalty": primer3_penalty,
            "hairpin_fwd_dg": 0.0,
            "hairpin_rev_dg": 0.0,
            "homodimer_fwd_dg": 0.0,
            "homodimer_rev_dg": 0.0,
            "heterodimer_dg": 0.0,
            "gc_clamp_fwd": True,
            "gc_clamp_rev": True,
            "poly_x_fwd": True,
            "poly_x_rev": True,
            "passes_qc": True,
            "rejection_reasons": [],
            "warnings": []  # v0.1.3: Separate warnings from failures
        }
        
        # 0. Sequence-level QC (GC Clamp, Poly-X) - v0.1.3
        # GC Clamp checks - now returns (passed, message, explanation)
        fwd_gc_ok, fwd_gc_msg, fwd_gc_explain = check_gc_clamp(fwd_seq)
        rev_gc_ok, rev_gc_msg, rev_gc_explain = check_gc_clamp(rev_seq)
        
        details["gc_clamp_fwd"] = fwd_gc_ok
        details["gc_clamp_rev"] = rev_gc_ok
        
        if not fwd_gc_ok:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Fwd: {fwd_gc_msg} - {fwd_gc_explain}")
        elif "Strong" in fwd_gc_msg:
            # Strong GC is a warning, not failure
            details["warnings"].append(f"Fwd: {fwd_gc_msg} - {fwd_gc_explain}")
        
        if not rev_gc_ok:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Rev: {rev_gc_msg} - {rev_gc_explain}")
        elif "Strong" in rev_gc_msg:
            details["warnings"].append(f"Rev: {rev_gc_msg} - {rev_gc_explain}")
        
        # Poly-X checks
        fwd_poly_ok, fwd_poly_msg = check_poly_x(fwd_seq)
        rev_poly_ok, rev_poly_msg = check_poly_x(rev_seq)
        
        details["poly_x_fwd"] = fwd_poly_ok
        details["poly_x_rev"] = rev_poly_ok
        
        if not fwd_poly_ok:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Fwd: {fwd_poly_msg}")
        
        if not rev_poly_ok:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Rev: {rev_poly_msg}")
        
        # Skip ViennaRNA checks if not available
        if not self.vienna.is_available:
            logger.debug("ViennaRNA not available, skipping secondary structure checks")
            return details["passes_qc"], details
        
        # 1. Hairpin checks
        fwd_fold = self.vienna.fold(fwd_seq)
        rev_fold = self.vienna.fold(rev_seq)
        
        fwd_hairpin_dg = fwd_fold.get("mfe", 0.0)
        rev_hairpin_dg = rev_fold.get("mfe", 0.0)
        
        details["hairpin_fwd_dg"] = fwd_hairpin_dg
        details["hairpin_rev_dg"] = rev_hairpin_dg
        
        if fwd_hairpin_dg < self.hairpin_dg_max:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Fwd hairpin too stable ({fwd_hairpin_dg:.1f} < {self.hairpin_dg_max})")
        
        if rev_hairpin_dg < self.hairpin_dg_max:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Rev hairpin too stable ({rev_hairpin_dg:.1f} < {self.hairpin_dg_max})")
        
        # 2. Homodimer checks
        fwd_homo = self.vienna.cofold(fwd_seq, fwd_seq)
        rev_homo = self.vienna.cofold(rev_seq, rev_seq)
        
        fwd_homo_dg = fwd_homo.get("mfe", 0.0)
        rev_homo_dg = rev_homo.get("mfe", 0.0)
        
        details["homodimer_fwd_dg"] = fwd_homo_dg
        details["homodimer_rev_dg"] = rev_homo_dg
        
        if fwd_homo_dg < self.homodimer_dg_max:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Fwd homodimer too stable ({fwd_homo_dg:.1f} < {self.homodimer_dg_max})")
        
        if rev_homo_dg < self.homodimer_dg_max:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Rev homodimer too stable ({rev_homo_dg:.1f} < {self.homodimer_dg_max})")
        
        # 3. Heterodimer check
        hetero = self.vienna.cofold(fwd_seq, rev_seq)
        hetero_dg = hetero.get("mfe", 0.0)
        
        details["heterodimer_dg"] = hetero_dg
        
        if hetero_dg < self.heterodimer_dg_max:
            details["passes_qc"] = False
            details["rejection_reasons"].append(f"Heterodimer too stable ({hetero_dg:.1f} < {self.heterodimer_dg_max})")
        
        return details["passes_qc"], details
    
    def rank_candidates(self, raw_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank all primer candidates from Primer3 results.
        
        Args:
            raw_results: Raw output from Primer3
            
        Returns:
            List of candidates sorted by quality (best first)
        """
        num_returned = raw_results.get('PRIMER_LEFT_NUM_RETURNED', 0)
        
        if num_returned == 0:
            return []
        
        candidates = []
        
        for i in range(num_returned):
            fwd_seq = raw_results.get(f'PRIMER_LEFT_{i}_SEQUENCE')
            rev_seq = raw_results.get(f'PRIMER_RIGHT_{i}_SEQUENCE')
            
            if not fwd_seq or not rev_seq:
                continue
            
            # Get Primer3 penalty score (lower is better)
            penalty = raw_results.get(f'PRIMER_PAIR_{i}_PENALTY', 0.0)
            
            # Evaluate with ViennaRNA
            passes_qc, details = self.evaluate_candidate(fwd_seq, rev_seq, penalty)
            
            candidates.append({
                "index": i,
                "fwd_seq": fwd_seq,
                "rev_seq": rev_seq,
                "fwd_tm": raw_results.get(f'PRIMER_LEFT_{i}_TM'),
                "rev_tm": raw_results.get(f'PRIMER_RIGHT_{i}_TM'),
                "fwd_gc": raw_results.get(f'PRIMER_LEFT_{i}_GC_PERCENT'),
                "rev_gc": raw_results.get(f'PRIMER_RIGHT_{i}_GC_PERCENT'),
                "fwd_pos": raw_results.get(f'PRIMER_LEFT_{i}'),
                "rev_pos": raw_results.get(f'PRIMER_RIGHT_{i}'),
                "product_size": raw_results.get(f'PRIMER_PAIR_{i}_PRODUCT_SIZE'),
                "primer3_penalty": penalty,
                "passes_qc": passes_qc,
                "qc_details": details
            })
        
        # Sort: QC-passing first, then by Primer3 penalty
        candidates.sort(key=lambda c: (not c["passes_qc"], c["primer3_penalty"]))
        
        logger.info(f"Evaluated {len(candidates)} candidates, {sum(1 for c in candidates if c['passes_qc'])} pass QC")
        
        return candidates
    
    def select_best(self, raw_results: Dict[str, Any]) -> Tuple[Optional[Dict], List[Dict]]:
        """
        Select the best primer pair and return alternatives.
        
        Returns:
            Tuple of (best_candidate, list_of_alternatives)
        """
        candidates = self.rank_candidates(raw_results)
        
        if not candidates:
            return None, []
        
        best = candidates[0]
        alternatives = candidates[1:self.show_alternatives + 1]
        
        if best["passes_qc"]:
            logger.info(f"Selected candidate #{best['index']} (passes QC, penalty={best['primer3_penalty']:.2f})")
        else:
            logger.warning(f"Best available candidate #{best['index']} does NOT pass QC: {best['qc_details'].get('rejection_reasons', [])}")
        
        return best, alternatives
