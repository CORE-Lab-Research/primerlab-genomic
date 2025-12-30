"""
SNP Position Validator (v0.6.0).

Analyzes SNP position within primer sequence and validates
for allele-specific PCR suitability.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple


@dataclass
class SnpPositionResult:
    """Result of SNP position analysis."""
    
    primer_sequence: str
    snp_index: int  # 0-indexed from 5' end
    snp_from_3prime: int  # 0-indexed from 3' end
    
    # Validation
    is_valid: bool
    is_optimal: bool  # 3' terminal
    is_acceptable: bool  # 3' -1 or -2
    
    # Context
    flanking_5: str  # 2 bases 5' of SNP
    flanking_3: str  # 2 bases 3' of SNP
    snp_base: str
    
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "primer_sequence": self.primer_sequence,
            "snp_index": self.snp_index,
            "snp_from_3prime": self.snp_from_3prime,
            "is_valid": self.is_valid,
            "is_optimal": self.is_optimal,
            "is_acceptable": self.is_acceptable,
            "flanking_5": self.flanking_5,
            "flanking_3": self.flanking_3,
            "snp_base": self.snp_base,
            "warnings": self.warnings,
        }


def validate_snp_position(
    primer_sequence: str,
    snp_index: int,
    max_distance_from_3prime: int = 4,
) -> bool:
    """
    Validate if SNP position is suitable for allele-specific PCR.
    
    Args:
        primer_sequence: Primer sequence (5'→3')
        snp_index: 0-indexed position of SNP from 5' end
        max_distance_from_3prime: Maximum allowed distance from 3' end
        
    Returns:
        True if SNP position is valid for discrimination
    """
    if snp_index < 0 or snp_index >= len(primer_sequence):
        return False
    
    # Calculate distance from 3' end
    distance_from_3prime = len(primer_sequence) - 1 - snp_index
    
    return distance_from_3prime <= max_distance_from_3prime


def analyze_snp_context(
    primer_sequence: str,
    snp_index: int,
) -> SnpPositionResult:
    """
    Analyze SNP position and flanking context in primer.
    
    Args:
        primer_sequence: Primer sequence (5'→3')
        snp_index: 0-indexed position of SNP from 5' end
        
    Returns:
        SnpPositionResult with detailed analysis
    """
    primer_sequence = primer_sequence.upper()
    primer_len = len(primer_sequence)
    
    warnings = []
    
    # Validate index
    if snp_index < 0 or snp_index >= primer_len:
        return SnpPositionResult(
            primer_sequence=primer_sequence,
            snp_index=snp_index,
            snp_from_3prime=-1,
            is_valid=False,
            is_optimal=False,
            is_acceptable=False,
            flanking_5="",
            flanking_3="",
            snp_base="",
            warnings=["SNP index out of range"],
        )
    
    # Calculate distance from 3' end
    snp_from_3prime = primer_len - 1 - snp_index
    
    # Get SNP base and flanking
    snp_base = primer_sequence[snp_index]
    
    flanking_5 = primer_sequence[max(0, snp_index - 2):snp_index]
    flanking_3 = primer_sequence[snp_index + 1:min(primer_len, snp_index + 3)]
    
    # Assess position
    is_optimal = snp_from_3prime == 0  # 3' terminal
    is_acceptable = snp_from_3prime <= 2  # Within 2 bases of 3'
    is_valid = snp_from_3prime <= 4  # Within 4 bases
    
    # Generate warnings
    if snp_from_3prime > 4:
        warnings.append(f"SNP is {snp_from_3prime} bases from 3' end - poor discrimination")
    elif snp_from_3prime > 2:
        warnings.append(f"SNP at position -{snp_from_3prime} from 3' - marginal discrimination")
    
    # Check for problematic flanking sequences
    context = flanking_5 + snp_base + flanking_3
    if "GGGG" in context or "CCCC" in context:
        warnings.append("Poly-G/C run near SNP may cause secondary structure")
    if "AAAA" in context or "TTTT" in context:
        warnings.append("Poly-A/T run near SNP may reduce specificity")
    
    return SnpPositionResult(
        primer_sequence=primer_sequence,
        snp_index=snp_index,
        snp_from_3prime=snp_from_3prime,
        is_valid=is_valid,
        is_optimal=is_optimal,
        is_acceptable=is_acceptable,
        flanking_5=flanking_5,
        flanking_3=flanking_3,
        snp_base=snp_base,
        warnings=warnings,
    )
