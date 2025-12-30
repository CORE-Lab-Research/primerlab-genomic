"""
Allele Discrimination Scoring Engine (v0.6.0).

Scores primers for SNP genotyping based on:
- SNP position in primer (3' end = best)
- Mismatch type (transition vs transversion)
- Thermodynamic stability
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple


# Mismatch type scoring
# Transversions (purine↔pyrimidine) discriminate better than transitions
MISMATCH_SCORES = {
    # Transitions (worse discrimination)
    ("A", "G"): 0.6,
    ("G", "A"): 0.6,
    ("C", "T"): 0.6,
    ("T", "C"): 0.6,
    # Transversions (better discrimination)
    ("A", "C"): 0.9,
    ("C", "A"): 0.9,
    ("A", "T"): 1.0,
    ("T", "A"): 1.0,
    ("G", "C"): 0.85,
    ("C", "G"): 0.85,
    ("G", "T"): 0.95,
    ("T", "G"): 0.95,
}

# Position weight (distance from 3' end)
# 0 = 3' terminal, 1 = 3'-1, etc.
POSITION_WEIGHTS = {
    0: 1.0,   # 3' terminal - best
    1: 0.7,   # 3'-1 position - good
    2: 0.4,   # 3'-2 position - acceptable
    3: 0.2,   # 3'-3 position - poor
}


@dataclass
class AlleleScoringResult:
    """Result of allele discrimination scoring."""
    
    primer_sequence: str
    snp_position: int  # 0-indexed from 3' end
    ref_allele: str
    alt_allele: str
    
    # Scores (0-100)
    position_score: float
    mismatch_score: float
    combined_score: float
    
    # Assessment
    grade: str  # A-F
    is_discriminating: bool
    warnings: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "primer_sequence": self.primer_sequence,
            "snp_position": self.snp_position,
            "ref_allele": self.ref_allele,
            "alt_allele": self.alt_allele,
            "position_score": round(self.position_score, 1),
            "mismatch_score": round(self.mismatch_score, 1),
            "combined_score": round(self.combined_score, 1),
            "grade": self.grade,
            "is_discriminating": self.is_discriminating,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
        }


def _get_position_weight(pos_from_3prime: int) -> float:
    """Get position weight for SNP distance from 3' end."""
    if pos_from_3prime in POSITION_WEIGHTS:
        return POSITION_WEIGHTS[pos_from_3prime]
    # Positions beyond 3 have minimal discrimination
    return max(0.05, 0.2 - (pos_from_3prime - 3) * 0.05)


def _get_mismatch_score(ref: str, alt: str) -> float:
    """Get mismatch type score."""
    ref = ref.upper()
    alt = alt.upper()
    return MISMATCH_SCORES.get((ref, alt), 0.5)


def _score_to_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def score_allele_discrimination(
    primer_sequence: str,
    snp_position: int,
    ref_allele: str,
    alt_allele: str,
    min_score_threshold: float = 60.0,
) -> AlleleScoringResult:
    """
    Score primer for allele-specific PCR discrimination.
    
    Args:
        primer_sequence: Primer sequence (5'→3')
        snp_position: Position of SNP from 3' end (0 = terminal)
        ref_allele: Reference allele at SNP position
        alt_allele: Alternative allele
        min_score_threshold: Minimum score to consider discriminating
        
    Returns:
        AlleleScoringResult with discrimination assessment
    """
    primer_sequence = primer_sequence.upper()
    ref_allele = ref_allele.upper()
    alt_allele = alt_allele.upper()
    
    warnings = []
    recommendations = []
    
    # Validate inputs
    if snp_position < 0 or snp_position >= len(primer_sequence):
        warnings.append(f"SNP position {snp_position} out of range")
        snp_position = 0  # Default to 3' end
    
    if len(ref_allele) != 1 or len(alt_allele) != 1:
        warnings.append("Only single nucleotide variants supported")
    
    # Calculate position score (0-100)
    position_weight = _get_position_weight(snp_position)
    position_score = position_weight * 100
    
    # Calculate mismatch type score (0-100)
    mismatch_weight = _get_mismatch_score(ref_allele, alt_allele)
    mismatch_score = mismatch_weight * 100
    
    # Combined score (weighted average)
    # Position matters more (60%) than mismatch type (40%)
    combined_score = (position_score * 0.6) + (mismatch_score * 0.4)
    
    # Generate warnings
    if snp_position > 3:
        warnings.append(f"SNP at position {snp_position} from 3' end - poor discrimination expected")
        recommendations.append("Move SNP closer to 3' end for better discrimination")
    
    if mismatch_weight < 0.7:
        warnings.append(f"{ref_allele}→{alt_allele} is a transition (less discriminating)")
        recommendations.append("Transversion mismatches (A↔T, G↔C) provide better specificity")
    
    # Grade and assessment
    grade = _score_to_grade(combined_score)
    is_discriminating = combined_score >= min_score_threshold
    
    if not is_discriminating:
        recommendations.append("Consider alternative primer design with SNP at 3' terminal position")
    
    return AlleleScoringResult(
        primer_sequence=primer_sequence,
        snp_position=snp_position,
        ref_allele=ref_allele,
        alt_allele=alt_allele,
        position_score=position_score,
        mismatch_score=mismatch_score,
        combined_score=combined_score,
        grade=grade,
        is_discriminating=is_discriminating,
        warnings=warnings,
        recommendations=recommendations,
    )
