"""
Exon Junction Detection (v0.6.0).

Detects if primers span exon-exon junctions for RT-qPCR specificity.
Primers spanning junctions will not amplify genomic DNA.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple


@dataclass
class ExonJunctionResult:
    """Result of exon junction analysis."""
    
    primer_sequence: str
    primer_start: int  # Position in transcript (0-indexed)
    primer_end: int
    
    # Junction detection
    spans_junction: bool
    junction_position: Optional[int]  # Position within primer
    exon_5prime: Optional[int]  # Exon number on 5' side
    exon_3prime: Optional[int]  # Exon number on 3' side
    
    # Quality
    junction_overlap_5: int  # Bases in 5' exon
    junction_overlap_3: int  # Bases in 3' exon
    is_optimal: bool  # Balanced overlap (>=5 bases each side)
    
    warnings: List[str]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "primer_sequence": self.primer_sequence,
            "primer_start": self.primer_start,
            "primer_end": self.primer_end,
            "spans_junction": self.spans_junction,
            "junction_position": self.junction_position,
            "exon_5prime": self.exon_5prime,
            "exon_3prime": self.exon_3prime,
            "junction_overlap_5": self.junction_overlap_5,
            "junction_overlap_3": self.junction_overlap_3,
            "is_optimal": self.is_optimal,
            "warnings": self.warnings,
        }


def find_junction_position(
    primer_start: int,
    primer_end: int,
    exon_boundaries: List[Tuple[int, int]],
) -> Optional[Tuple[int, int, int]]:
    """
    Find if primer spans an exon junction.
    
    Args:
        primer_start: Start position in transcript (0-indexed)
        primer_end: End position (exclusive)
        exon_boundaries: List of (start, end) for each exon
        
    Returns:
        Tuple of (junction_pos_in_primer, exon_5prime_idx, exon_3prime_idx) or None
    """
    # Sort exons by start position
    sorted_exons = sorted(enumerate(exon_boundaries), key=lambda x: x[1][0])
    
    for i, (exon_idx, (exon_start, exon_end)) in enumerate(sorted_exons):
        # Check if primer end is past this exon end
        if primer_start < exon_end <= primer_end:
            # Primer spans this junction
            junction_pos_in_primer = exon_end - primer_start
            
            # Find next exon
            if i + 1 < len(sorted_exons):
                next_exon_idx = sorted_exons[i + 1][0]
                return (junction_pos_in_primer, exon_idx, next_exon_idx)
    
    return None


def detect_exon_junction(
    primer_sequence: str,
    primer_start: int,
    exon_boundaries: List[Tuple[int, int]],
    min_overlap: int = 5,
) -> ExonJunctionResult:
    """
    Detect if primer spans an exon-exon junction.
    
    Args:
        primer_sequence: Primer sequence
        primer_start: Start position in transcript (0-indexed)
        exon_boundaries: List of (start, end) for each exon in transcript
        min_overlap: Minimum bases overlapping each exon for optimal
        
    Returns:
        ExonJunctionResult with junction analysis
    """
    primer_sequence = primer_sequence.upper()
    primer_len = len(primer_sequence)
    primer_end = primer_start + primer_len
    
    warnings = []
    
    # Find junction
    junction_info = find_junction_position(primer_start, primer_end, exon_boundaries)
    
    if junction_info is None:
        # No junction spanned
        # Determine which exon primer is in
        current_exon = None
        for idx, (exon_start, exon_end) in enumerate(exon_boundaries):
            if exon_start <= primer_start < exon_end:
                current_exon = idx
                break
        
        warnings.append("Primer does not span exon junction - may amplify gDNA")
        
        return ExonJunctionResult(
            primer_sequence=primer_sequence,
            primer_start=primer_start,
            primer_end=primer_end,
            spans_junction=False,
            junction_position=None,
            exon_5prime=current_exon,
            exon_3prime=current_exon,
            junction_overlap_5=0,
            junction_overlap_3=0,
            is_optimal=False,
            warnings=warnings,
        )
    
    junction_pos, exon_5prime, exon_3prime = junction_info
    
    # Calculate overlap on each side
    overlap_5 = junction_pos
    overlap_3 = primer_len - junction_pos
    
    is_optimal = overlap_5 >= min_overlap and overlap_3 >= min_overlap
    
    if not is_optimal:
        if overlap_5 < min_overlap:
            warnings.append(f"Only {overlap_5} bp overlap in 5' exon (min: {min_overlap})")
        if overlap_3 < min_overlap:
            warnings.append(f"Only {overlap_3} bp overlap in 3' exon (min: {min_overlap})")
    
    return ExonJunctionResult(
        primer_sequence=primer_sequence,
        primer_start=primer_start,
        primer_end=primer_end,
        spans_junction=True,
        junction_position=junction_pos,
        exon_5prime=exon_5prime,
        exon_3prime=exon_3prime,
        junction_overlap_5=overlap_5,
        junction_overlap_3=overlap_3,
        is_optimal=is_optimal,
        warnings=warnings,
    )
