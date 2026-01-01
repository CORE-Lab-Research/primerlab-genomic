"""
Nested PCR Data Models.

Data structures for nested PCR primer design results.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class NestedPrimerSet:
    """
    Complete nested PCR primer set with outer and inner pairs.
    """
    # Outer primers (required)
    outer_forward: str
    outer_reverse: str
    outer_tm_forward: float
    outer_tm_reverse: float
    outer_gc_forward: float
    outer_gc_reverse: float
    outer_start: int
    outer_end: int
    outer_product_size: int
    
    # Inner primers (required)
    inner_forward: str
    inner_reverse: str
    inner_tm_forward: float
    inner_tm_reverse: float
    inner_gc_forward: float
    inner_gc_reverse: float
    inner_start: int
    inner_end: int
    inner_product_size: int
    
    # Optional fields with defaults
    outer_amplicon_seq: str = ""
    inner_amplicon_seq: str = ""
    outer_score: float = 0.0
    inner_score: float = 0.0
    combined_score: float = 0.0
    grade: str = "C"
    
    def get_tm_difference(self) -> float:
        """Get Tm difference between inner and outer primers."""
        outer_avg = (self.outer_tm_forward + self.outer_tm_reverse) / 2
        inner_avg = (self.inner_tm_forward + self.inner_tm_reverse) / 2
        return inner_avg - outer_avg
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "outer": {
                "forward": self.outer_forward,
                "reverse": self.outer_reverse,
                "tm_forward": self.outer_tm_forward,
                "tm_reverse": self.outer_tm_reverse,
                "gc_forward": self.outer_gc_forward,
                "gc_reverse": self.outer_gc_reverse,
                "product_size": self.outer_product_size,
                "start": self.outer_start,
                "end": self.outer_end,
            },
            "inner": {
                "forward": self.inner_forward,
                "reverse": self.inner_reverse,
                "tm_forward": self.inner_tm_forward,
                "tm_reverse": self.inner_tm_reverse,
                "gc_forward": self.inner_gc_forward,
                "gc_reverse": self.inner_gc_reverse,
                "product_size": self.inner_product_size,
                "start": self.inner_start,
                "end": self.inner_end,
            },
            "score": self.combined_score,
            "grade": self.grade,
            "tm_difference": self.get_tm_difference(),
        }


@dataclass
class NestedPCRResult:
    """
    Complete result of nested PCR primer design.
    """
    success: bool = False
    primer_set: Optional[NestedPrimerSet] = None
    alternatives: List[NestedPrimerSet] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    outer_size_range: tuple = (400, 600)
    inner_size_range: tuple = (100, 200)
    sequence_length: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "primer_set": self.primer_set.to_dict() if self.primer_set else None,
            "alternatives_count": len(self.alternatives),
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "parameters": {
                "outer_size_range": self.outer_size_range,
                "inner_size_range": self.inner_size_range,
                "sequence_length": self.sequence_length,
            }
        }
