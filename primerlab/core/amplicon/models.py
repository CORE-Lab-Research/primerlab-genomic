"""
Amplicon Analysis Models.

Data structures for amplicon quality analysis results.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple


@dataclass
class SecondaryStructure:
    """Result of secondary structure prediction."""
    sequence: str
    structure: str  # Dot-bracket notation
    delta_g: float  # kcal/mol
    is_problematic: bool = False
    problematic_regions: List[Tuple[int, int]] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "sequence": self.sequence,
            "structure": self.structure,
            "delta_g": self.delta_g,
            "is_problematic": self.is_problematic,
            "problematic_regions": self.problematic_regions
        }


@dataclass
class GCProfile:
    """GC content profile across amplicon."""
    positions: List[int]
    gc_values: List[float]
    window_size: int
    step_size: int
    uniformity_score: float  # 0-100
    min_gc: float
    max_gc: float
    avg_gc: float
    
    def to_dict(self) -> Dict:
        return {
            "positions": self.positions,
            "gc_values": self.gc_values,
            "window_size": self.window_size,
            "step_size": self.step_size,
            "uniformity_score": self.uniformity_score,
            "min_gc": self.min_gc,
            "max_gc": self.max_gc,
            "avg_gc": self.avg_gc
        }


@dataclass
class GCClamp:
    """GC clamp analysis at amplicon ends."""
    five_prime_count: int  # G/C count at 5' end
    three_prime_count: int  # G/C count at 3' end
    region_size: int
    is_optimal: bool
    warning: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "five_prime_count": self.five_prime_count,
            "three_prime_count": self.three_prime_count,
            "region_size": self.region_size,
            "is_optimal": self.is_optimal,
            "warning": self.warning
        }


@dataclass  
class AmpliconTm:
    """Amplicon melting temperature prediction."""
    tm: float
    method: str = "nearest-neighbor"
    na_concentration: float = 50.0
    width: float = 0.0  # Melting curve sharpness (lower = sharper)
    
    def to_dict(self) -> Dict:
        return {
            "tm": self.tm,
            "method": self.method,
            "na_concentration": self.na_concentration,
            "width": self.width
        }


@dataclass
class RestrictionSite:
    """A restriction enzyme recognition site."""
    enzyme: str
    position: int
    recognition_seq: str
    cut_position: int  # Relative to recognition start
    
    def to_dict(self) -> Dict:
        return {
            "enzyme": self.enzyme,
            "position": self.position,
            "recognition_seq": self.recognition_seq,
            "cut_position": self.cut_position
        }


@dataclass
class AmpliconQuality:
    """Overall amplicon quality assessment."""
    score: float  # 0-100
    grade: str  # A-F
    structure_score: float
    gc_uniformity_score: float
    gc_clamp_score: float
    length_score: float
    tm_sharpness_score: float
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "grade": self.grade,
            "components": {
                "structure": self.structure_score,
                "gc_uniformity": self.gc_uniformity_score,
                "gc_clamp": self.gc_clamp_score,
                "length": self.length_score,
                "tm_sharpness": self.tm_sharpness_score
            },
            "warnings": self.warnings
        }


@dataclass
class AmpliconAnalysisResult:
    """Complete amplicon analysis result."""
    sequence: str
    length: int
    secondary_structure: Optional[SecondaryStructure] = None
    gc_profile: Optional[GCProfile] = None
    gc_clamp: Optional[GCClamp] = None
    amplicon_tm: Optional[AmpliconTm] = None
    restriction_sites: List[RestrictionSite] = field(default_factory=list)
    quality: Optional[AmpliconQuality] = None
    
    def to_dict(self) -> Dict:
        result = {
            "sequence": self.sequence,
            "length": self.length
        }
        if self.secondary_structure:
            result["secondary_structure"] = self.secondary_structure.to_dict()
        if self.gc_profile:
            result["gc_profile"] = self.gc_profile.to_dict()
        if self.gc_clamp:
            result["gc_clamp"] = self.gc_clamp.to_dict()
        if self.amplicon_tm:
            result["amplicon_tm"] = self.amplicon_tm.to_dict()
        if self.restriction_sites:
            result["restriction_sites"] = [rs.to_dict() for rs in self.restriction_sites]
        if self.quality:
            result["quality"] = self.quality.to_dict()
        return result
