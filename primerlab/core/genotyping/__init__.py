"""
Genotyping Module (v0.6.0).

Provides allele discrimination scoring for SNP genotyping assays,
including allele-specific PCR primer validation.
"""

from .allele_scoring import (
    score_allele_discrimination,
    AlleleScoringResult,
)
from .snp_position import (
    validate_snp_position,
    analyze_snp_context,
    SnpPositionResult,
)
from .discrimination_tm import (
    calculate_discrimination_tm,
    estimate_allele_specificity,
)

__all__ = [
    # Allele scoring
    "score_allele_discrimination",
    "AlleleScoringResult",
    # SNP position
    "validate_snp_position",
    "analyze_snp_context",
    "SnpPositionResult",
    # Discrimination Tm
    "calculate_discrimination_tm",
    "estimate_allele_specificity",
]
