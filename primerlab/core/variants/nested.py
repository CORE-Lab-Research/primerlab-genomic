"""
Nested PCR Engine.

Designs nested PCR primer sets with outer and inner primer pairs.
"""

from typing import Dict, Any, Optional, List, Tuple
from primerlab.core.variants.models import NestedPrimerSet, NestedPCRResult
from primerlab.core.tools.primer3_wrapper import Primer3Wrapper
from primerlab.core.logger import get_logger

logger = get_logger()


class NestedPCREngine:
    """
    Engine for designing nested PCR primers.
    
    Nested PCR uses two sets of primers:
    - Outer primers: First round PCR (larger product)
    - Inner primers: Second round PCR within outer product
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize nested PCR engine.
        
        Args:
            config: Optional configuration dict
        """
        self.config = config or {}
        self.p3_wrapper = Primer3Wrapper()
        
        # Default size ranges
        self.outer_size_min = self.config.get("outer_size_min", 400)
        self.outer_size_max = self.config.get("outer_size_max", 600)
        self.inner_size_min = self.config.get("inner_size_min", 100)
        self.inner_size_max = self.config.get("inner_size_max", 200)
        
        # Tm settings
        self.outer_tm_opt = self.config.get("outer_tm_opt", 58.0)
        self.inner_tm_opt = self.config.get("inner_tm_opt", 60.0)  # Slightly higher
        
    def design(self, sequence: str) -> NestedPCRResult:
        """
        Design nested PCR primer set.
        
        Args:
            sequence: Template sequence
            
        Returns:
            NestedPCRResult with primer set
        """
        logger.info(f"Designing nested PCR primers for {len(sequence)}bp sequence")
        
        result = NestedPCRResult(
            sequence_length=len(sequence),
            outer_size_range=(self.outer_size_min, self.outer_size_max),
            inner_size_range=(self.inner_size_min, self.inner_size_max),
        )
        
        # Validate sequence length
        if len(sequence) < self.outer_size_min + 50:
            result.warnings.append(
                f"Sequence too short ({len(sequence)}bp) for nested PCR. "
                f"Minimum recommended: {self.outer_size_min + 50}bp"
            )
            return result
        
        # Step 1: Design outer primers
        logger.info("Step 1: Designing outer primers...")
        outer_primers = self._design_outer_primers(sequence)
        
        if not outer_primers:
            result.warnings.append("Failed to design outer primers")
            result.recommendations.append("Try increasing sequence length or adjusting size range")
            return result
        
        logger.info(f"Found {len(outer_primers)} outer primer candidates")
        
        # Step 2: Design inner primers for each outer pair
        logger.info("Step 2: Designing inner primers within outer amplicons...")
        nested_sets: List[NestedPrimerSet] = []
        
        for outer in outer_primers[:5]:  # Top 5 outer candidates
            outer_amplicon = self._extract_amplicon(
                sequence, 
                outer["start"], 
                outer["end"]
            )
            
            if len(outer_amplicon) < self.inner_size_min + 20:
                continue
                
            inner_primers = self._design_inner_primers(outer_amplicon)
            
            if inner_primers:
                # Create nested set
                for inner in inner_primers[:3]:  # Top 3 inner per outer
                    nested_set = self._create_nested_set(
                        sequence, outer, inner, outer_amplicon
                    )
                    if nested_set:
                        nested_sets.append(nested_set)
        
        if not nested_sets:
            result.warnings.append("Failed to design inner primers within outer amplicons")
            result.recommendations.append("Try adjusting inner size range or Tm settings")
            return result
        
        # Step 3: Score and select best
        logger.info(f"Step 3: Scoring {len(nested_sets)} nested primer sets...")
        nested_sets = self._score_nested_sets(nested_sets)
        nested_sets.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Set result
        result.success = True
        result.primer_set = nested_sets[0]
        result.alternatives = nested_sets[1:5]  # Top 4 alternatives
        
        # Add recommendations
        if result.primer_set.get_tm_difference() < 1.0:
            result.recommendations.append(
                "Consider increasing inner primer Tm for better specificity"
            )
        
        logger.info(f"Nested PCR design complete. Grade: {result.primer_set.grade}")
        return result
    
    def _design_outer_primers(self, sequence: str) -> List[Dict[str, Any]]:
        """Design outer primer pairs."""
        config = {
            "parameters": {
                "product_size_range": [[self.outer_size_min, self.outer_size_max]],
                "tm": {
                    "min": self.outer_tm_opt - 3,
                    "opt": self.outer_tm_opt,
                    "max": self.outer_tm_opt + 3,
                },
                "primer_size": {"min": 18, "opt": 20, "max": 25},
            }
        }
        
        raw_results = self.p3_wrapper.design_primers(sequence, config)
        return self._parse_primer3_results(raw_results, sequence)
    
    def _design_inner_primers(self, amplicon: str) -> List[Dict[str, Any]]:
        """Design inner primer pairs within outer amplicon."""
        config = {
            "parameters": {
                "product_size_range": [[self.inner_size_min, self.inner_size_max]],
                "tm": {
                    "min": self.inner_tm_opt - 3,
                    "opt": self.inner_tm_opt,
                    "max": self.inner_tm_opt + 3,
                },
                "primer_size": {"min": 18, "opt": 20, "max": 25},
            }
        }
        
        raw_results = self.p3_wrapper.design_primers(amplicon, config)
        return self._parse_primer3_results(raw_results, amplicon)
    
    def _parse_primer3_results(
        self, 
        raw_results: Dict[str, Any],
        sequence: str
    ) -> List[Dict[str, Any]]:
        """Parse Primer3 results into primer list."""
        primers = []
        num_returned = raw_results.get("PRIMER_LEFT_NUM_RETURNED", 0)
        
        for i in range(num_returned):
            try:
                fwd_pos = raw_results.get(f"PRIMER_LEFT_{i}", (0, 0))
                rev_pos = raw_results.get(f"PRIMER_RIGHT_{i}", (0, 0))
                
                fwd_start, fwd_len = fwd_pos
                rev_start, rev_len = rev_pos
                
                primers.append({
                    "index": i,
                    "fwd_seq": raw_results.get(f"PRIMER_LEFT_{i}_SEQUENCE", ""),
                    "rev_seq": raw_results.get(f"PRIMER_RIGHT_{i}_SEQUENCE", ""),
                    "fwd_tm": raw_results.get(f"PRIMER_LEFT_{i}_TM", 0.0),
                    "rev_tm": raw_results.get(f"PRIMER_RIGHT_{i}_TM", 0.0),
                    "fwd_gc": raw_results.get(f"PRIMER_LEFT_{i}_GC_PERCENT", 0.0),
                    "rev_gc": raw_results.get(f"PRIMER_RIGHT_{i}_GC_PERCENT", 0.0),
                    "start": fwd_start,
                    "end": rev_start,
                    "product_size": raw_results.get(f"PRIMER_PAIR_{i}_PRODUCT_SIZE", 0),
                })
            except (KeyError, TypeError):
                continue
        
        return primers
    
    def _extract_amplicon(self, sequence: str, start: int, end: int) -> str:
        """Extract amplicon sequence."""
        if 0 <= start < len(sequence) and start < end <= len(sequence):
            return sequence[start:end]
        return ""
    
    def _create_nested_set(
        self,
        sequence: str,
        outer: Dict[str, Any],
        inner: Dict[str, Any],
        outer_amplicon: str
    ) -> Optional[NestedPrimerSet]:
        """Create NestedPrimerSet from outer and inner primer dicts."""
        try:
            inner_amplicon = self._extract_amplicon(
                outer_amplicon, inner["start"], inner["end"]
            )
            
            return NestedPrimerSet(
                # Outer
                outer_forward=outer["fwd_seq"],
                outer_reverse=outer["rev_seq"],
                outer_tm_forward=outer["fwd_tm"],
                outer_tm_reverse=outer["rev_tm"],
                outer_gc_forward=outer["fwd_gc"],
                outer_gc_reverse=outer["rev_gc"],
                outer_start=outer["start"],
                outer_end=outer["end"],
                outer_product_size=outer["product_size"],
                outer_amplicon_seq=outer_amplicon,
                # Inner
                inner_forward=inner["fwd_seq"],
                inner_reverse=inner["rev_seq"],
                inner_tm_forward=inner["fwd_tm"],
                inner_tm_reverse=inner["rev_tm"],
                inner_gc_forward=inner["fwd_gc"],
                inner_gc_reverse=inner["rev_gc"],
                inner_start=inner["start"],
                inner_end=inner["end"],
                inner_product_size=inner["product_size"],
                inner_amplicon_seq=inner_amplicon,
            )
        except (KeyError, TypeError) as e:
            logger.warning(f"Failed to create nested set: {e}")
            return None
    
    def _score_nested_sets(
        self, 
        nested_sets: List[NestedPrimerSet]
    ) -> List[NestedPrimerSet]:
        """Score nested primer sets."""
        for ns in nested_sets:
            # Scoring factors
            score = 100.0
            
            # Tm uniformity within pairs (max -20)
            outer_tm_diff = abs(ns.outer_tm_forward - ns.outer_tm_reverse)
            inner_tm_diff = abs(ns.inner_tm_forward - ns.inner_tm_reverse)
            score -= min(outer_tm_diff * 5, 10)
            score -= min(inner_tm_diff * 5, 10)
            
            # Inner Tm should be >= outer Tm (max -10)
            tm_boost = ns.get_tm_difference()
            if tm_boost < 0:
                score -= min(abs(tm_boost) * 5, 10)
            elif tm_boost > 4:
                score -= min((tm_boost - 4) * 2, 5)
            
            # GC content 40-60% ideal (max -10)
            for gc in [ns.outer_gc_forward, ns.outer_gc_reverse, 
                       ns.inner_gc_forward, ns.inner_gc_reverse]:
                if gc < 40 or gc > 60:
                    score -= 2.5
            
            # Size ratio (inner should be ~30-50% of outer) (max -10)
            size_ratio = ns.inner_product_size / ns.outer_product_size
            if size_ratio < 0.2 or size_ratio > 0.6:
                score -= 5
            
            ns.combined_score = max(score, 0)
            ns.outer_score = score  # Simplified
            ns.inner_score = score  # Simplified
            
            # Grade
            if score >= 90:
                ns.grade = "A"
            elif score >= 80:
                ns.grade = "B"
            elif score >= 70:
                ns.grade = "C"
            elif score >= 60:
                ns.grade = "D"
            else:
                ns.grade = "F"
        
        return nested_sets


def design_nested_primers(
    sequence: str,
    outer_size_range: Tuple[int, int] = (400, 600),
    inner_size_range: Tuple[int, int] = (100, 200),
    outer_tm: float = 58.0,
    inner_tm: float = 60.0,
) -> NestedPCRResult:
    """
    Design nested PCR primers.
    
    Args:
        sequence: Template sequence
        outer_size_range: (min, max) for outer amplicon
        inner_size_range: (min, max) for inner amplicon
        outer_tm: Optimal Tm for outer primers
        inner_tm: Optimal Tm for inner primers
        
    Returns:
        NestedPCRResult with primer set
    """
    config = {
        "outer_size_min": outer_size_range[0],
        "outer_size_max": outer_size_range[1],
        "inner_size_min": inner_size_range[0],
        "inner_size_max": inner_size_range[1],
        "outer_tm_opt": outer_tm,
        "inner_tm_opt": inner_tm,
    }
    
    engine = NestedPCREngine(config)
    return engine.design(sequence)
