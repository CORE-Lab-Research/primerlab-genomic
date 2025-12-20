"""
BLAST Result Models (v0.3.0)

Data classes for representing BLAST search results and hits.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class AlignmentMethod(Enum):
    """Method used for alignment/search."""
    BLAST = "blast"
    BIOPYTHON = "biopython"
    NCBI_WEB = "ncbi_web"


@dataclass
class BlastHit:
    """
    Represents a single BLAST hit (alignment).
    
    Attributes:
        subject_id: ID of the database sequence
        subject_title: Description of the subject sequence
        query_start: Start position on query (1-indexed)
        query_end: End position on query (1-indexed)
        subject_start: Start position on subject (1-indexed)
        subject_end: End position on subject (1-indexed)
        identity_percent: Percentage identity (0-100)
        alignment_length: Length of the alignment
        mismatches: Number of mismatches
        gaps: Number of gaps
        evalue: Expect value
        bit_score: Bit score
        query_seq: Aligned query sequence
        subject_seq: Aligned subject sequence
        is_on_target: True if this is the expected target
    """
    subject_id: str
    subject_title: str
    query_start: int
    query_end: int
    subject_start: int
    subject_end: int
    identity_percent: float
    alignment_length: int
    mismatches: int
    gaps: int
    evalue: float
    bit_score: float
    query_seq: str = ""
    subject_seq: str = ""
    is_on_target: bool = False
    
    @property
    def coverage_percent(self) -> float:
        """Calculate query coverage percentage."""
        query_len = self.query_end - self.query_start + 1
        return (self.alignment_length / query_len) * 100 if query_len > 0 else 0.0
    
    def is_significant(self, evalue_threshold: float = 1e-5, identity_threshold: float = 80.0) -> bool:
        """Check if hit is significant based on e-value and identity."""
        return self.evalue <= evalue_threshold and self.identity_percent >= identity_threshold


@dataclass
class BlastResult:
    """
    Complete result of a BLAST search for a primer.
    
    Attributes:
        query_id: ID of the query sequence (primer name)
        query_seq: Query sequence
        query_length: Length of query
        hits: List of BlastHit objects
        method: Method used for search
        database: Database searched against
        parameters: Search parameters used
        success: Whether search completed successfully
        error: Error message if failed
    """
    query_id: str
    query_seq: str
    query_length: int
    hits: List[BlastHit] = field(default_factory=list)
    method: AlignmentMethod = AlignmentMethod.BLAST
    database: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    
    @property
    def hit_count(self) -> int:
        """Total number of hits."""
        return len(self.hits)
    
    @property
    def significant_hits(self) -> List[BlastHit]:
        """Get significant hits only."""
        return [h for h in self.hits if h.is_significant()]
    
    @property
    def off_target_hits(self) -> List[BlastHit]:
        """Get off-target (non-specific) hits."""
        return [h for h in self.hits if not h.is_on_target]
    
    @property
    def on_target_hit(self) -> Optional[BlastHit]:
        """Get the on-target hit if exists."""
        for h in self.hits:
            if h.is_on_target:
                return h
        return None
    
    def get_specificity_score(self) -> float:
        """
        Calculate specificity score (0-100).
        
        100 = Only on-target hit
        0 = Many significant off-target hits
        """
        if not self.hits:
            return 100.0  # No hits = specific (or no database)
        
        on_target = self.on_target_hit
        off_targets = [h for h in self.significant_hits if not h.is_on_target]
        
        if not off_targets:
            return 100.0
        
        # Penalize based on number and quality of off-targets
        penalty = 0.0
        for hit in off_targets:
            # Higher identity = higher penalty
            penalty += hit.identity_percent / 100.0 * 20
        
        score = max(0.0, 100.0 - penalty)
        return round(score, 1)


@dataclass
class SpecificityResult:
    """
    Combined specificity result for a primer pair.
    
    Attributes:
        forward_result: BLAST result for forward primer
        reverse_result: BLAST result for reverse primer
        combined_score: Overall specificity score
        is_specific: True if both primers are specific
        warnings: List of specificity warnings
    """
    forward_result: BlastResult
    reverse_result: BlastResult
    combined_score: float = 0.0
    is_specific: bool = True
    warnings: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Calculate combined score after initialization."""
        fwd_score = self.forward_result.get_specificity_score()
        rev_score = self.reverse_result.get_specificity_score()
        self.combined_score = (fwd_score + rev_score) / 2
        
        # Check specificity
        if fwd_score < 80:
            self.is_specific = False
            self.warnings.append(f"Forward primer has low specificity ({fwd_score:.1f})")
        if rev_score < 80:
            self.is_specific = False
            self.warnings.append(f"Reverse primer has low specificity ({rev_score:.1f})")
