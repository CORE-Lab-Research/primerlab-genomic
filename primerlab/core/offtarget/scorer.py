"""
Specificity Scorer (v0.3.0)

Advanced specificity scoring for primers based on off-target analysis.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple

from primerlab.core.logger import get_logger
from primerlab.core.offtarget.finder import OfftargetResult, PrimerPairOfftargetResult, OfftargetHit

logger = get_logger()


@dataclass
class SpecificityScore:
    """
    Detailed specificity score breakdown.
    
    Attributes:
        overall_score: Combined specificity score (0-100)
        binding_score: Score based on off-target binding sites
        mismatch_score: Score based on 3' mismatches
        product_score: Score based on potential products
        grade: 'A', 'B', 'C', 'D', or 'F'
        is_acceptable: True if score >= threshold
        details: Detailed breakdown
    """
    overall_score: float
    binding_score: float = 100.0
    mismatch_score: float = 100.0
    product_score: float = 100.0
    grade: str = "A"
    is_acceptable: bool = True
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate grade based on overall score."""
        if self.overall_score >= 90:
            self.grade = "A"
        elif self.overall_score >= 80:
            self.grade = "B"
        elif self.overall_score >= 70:
            self.grade = "C"
        elif self.overall_score >= 60:
            self.grade = "D"
        else:
            self.grade = "F"

        self.is_acceptable = self.overall_score >= 70


class SpecificityScorer:
    """
    Calculate detailed specificity scores for primers.
    
    v0.3.0: Considers multiple factors for specificity assessment.
    
    Scoring Factors:
    - Number and quality of off-target hits
    - 3' end mismatches (critical for extension)
    - Potential off-target products
    - E-value and identity distribution
    """

    # Scoring weights
    WEIGHTS = {
        "binding": 0.5,    # Weight for off-target binding
        "mismatch": 0.3,   # Weight for 3' mismatch analysis
        "product": 0.2,    # Weight for potential products
    }

    # Penalties per off-target by risk level
    PENALTIES = {
        "high": 20.0,
        "medium": 10.0,
        "low": 3.0,
    }

    def __init__(self, threshold: float = 70.0):
        """
        Initialize scorer.
        
        Args:
            threshold: Minimum acceptable score
        """
        self.threshold = threshold

    def score_primer(self, offtarget_result: OfftargetResult) -> SpecificityScore:
        """
        Score a single primer's specificity.
        
        Args:
            offtarget_result: Off-target analysis result
            
        Returns:
            SpecificityScore with breakdown
        """
        # Calculate binding score
        binding_score = self._calculate_binding_score(offtarget_result.offtargets)

        # Calculate mismatch score (based on 3' considerations)
        mismatch_score = self._calculate_mismatch_score(offtarget_result.offtargets)

        # No product score for single primer
        product_score = 100.0

        # Weighted average
        overall = (
            binding_score * self.WEIGHTS["binding"] +
            mismatch_score * self.WEIGHTS["mismatch"] +
            product_score * self.WEIGHTS["product"]
        )

        # Normalize to 0-100
        overall = min(100.0, max(0.0, overall))

        return SpecificityScore(
            overall_score=round(overall, 1),
            binding_score=round(binding_score, 1),
            mismatch_score=round(mismatch_score, 1),
            product_score=round(product_score, 1),
            is_acceptable=overall >= self.threshold,
            details={
                "offtarget_count": offtarget_result.offtarget_count,
                "significant_count": offtarget_result.significant_offtargets,
                "high_risk_count": sum(1 for ot in offtarget_result.offtargets if ot.risk_level == "high"),
            }
        )

    def score_primer_pair(
        self,
        pair_result: PrimerPairOfftargetResult
    ) -> Tuple[SpecificityScore, SpecificityScore, SpecificityScore]:
        """
        Score a primer pair's specificity (and optional probe).
        
        Args:
            pair_result: Primer pair off-target result (potentially containing probe_result)
            
        Returns:
            Tuple of (forward_score, reverse_score, combined_score)
        """
        # Score individual primers
        fwd_score = self.score_primer(pair_result.forward_result)
        rev_score = self.score_primer(pair_result.reverse_result)
        
        probe_score = None
        if pair_result.probe_result:
            probe_score = self.score_primer(pair_result.probe_result)

        # Calculate combined with product penalty
        product_score = self._calculate_product_score(pair_result.potential_products)

        if probe_score:
            combined_overall = (
                fwd_score.overall_score * 0.3 +
                rev_score.overall_score * 0.3 +
                probe_score.overall_score * 0.2 +
                product_score * 0.2
            )
            binding_score = (fwd_score.binding_score + rev_score.binding_score + probe_score.binding_score) / 3
            mismatch_score = (fwd_score.mismatch_score + rev_score.mismatch_score + probe_score.mismatch_score) / 3
        else:
            combined_overall = (
                fwd_score.overall_score * 0.4 +
                rev_score.overall_score * 0.4 +
                product_score * 0.2
            )
            binding_score = (fwd_score.binding_score + rev_score.binding_score) / 2
            mismatch_score = (fwd_score.mismatch_score + rev_score.mismatch_score) / 2

        combined = SpecificityScore(
            overall_score=round(combined_overall, 1),
            binding_score=round(binding_score, 1),
            mismatch_score=round(mismatch_score, 1),
            product_score=round(product_score, 1),
            is_acceptable=combined_overall >= self.threshold,
            details={
                "forward_score": fwd_score.overall_score,
                "reverse_score": rev_score.overall_score,
                "probe_score": probe_score.overall_score if probe_score else None,
                "potential_products": pair_result.potential_products,
            }
        )

        return (fwd_score, rev_score, combined)

    def _calculate_binding_score(self, offtargets: List[OfftargetHit]) -> float:
        """Calculate score based on off-target binding sites."""
        if not offtargets:
            return 100.0

        penalty = 0.0
        for ot in offtargets:
            penalty += self.PENALTIES.get(ot.risk_level, 5.0)

        return max(0.0, 100.0 - penalty)

    def _calculate_mismatch_score(self, offtargets: List[OfftargetHit]) -> float:
        """
        Calculate score based on 3' mismatch patterns.
        
        Off-targets with mismatches at 3' end are less likely to extend.
        """
        if not offtargets:
            return 100.0

        # Penalize more for off-targets with few mismatches
        # (meaning they could still extend)
        penalty = 0.0
        for ot in offtargets:
            if ot.mismatches == 0:
                penalty += 15.0  # Perfect match = high risk
            elif ot.mismatches == 1:
                penalty += 8.0
            elif ot.mismatches == 2:
                penalty += 4.0
            else:
                penalty += 1.0

        return max(0.0, 100.0 - penalty)

    def _calculate_product_score(self, potential_products: int) -> float:
        """Calculate score based on potential off-target products."""
        if potential_products == 0:
            return 100.0
        elif potential_products == 1:
            return 70.0
        elif potential_products <= 3:
            return 50.0
        else:
            return max(0.0, 100.0 - potential_products * 15)


def calculate_specificity(
    offtarget_result: OfftargetResult,
    threshold: float = 70.0
) -> SpecificityScore:
    """
    Convenience function to calculate specificity score.
    
    Args:
        offtarget_result: Off-target analysis result
        threshold: Minimum acceptable score
        
    Returns:
        SpecificityScore
    """
    scorer = SpecificityScorer(threshold=threshold)
    return scorer.score_primer(offtarget_result)
