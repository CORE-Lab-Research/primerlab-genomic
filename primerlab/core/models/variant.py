"""
Variant Data Models (v0.3.1)

Data classes for SNP/variant representation and overlap detection.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class VariantType(Enum):
    """Types of genetic variants."""
    SNP = "snp"           # Single nucleotide polymorphism
    INSERTION = "ins"     # Insertion
    DELETION = "del"      # Deletion
    MNP = "mnp"           # Multi-nucleotide polymorphism
    COMPLEX = "complex"   # Complex variant


class VariantImpact(Enum):
    """Impact level for primer design."""
    HIGH = "high"         # Variant at 3' end or critical position
    MEDIUM = "medium"     # Variant in middle of primer
    LOW = "low"           # Variant at 5' end (less critical)
    NONE = "none"         # No impact


@dataclass
class Variant:
    """
    Represents a single genetic variant.
    
    Attributes:
        chrom: Chromosome name
        pos: 1-based position
        ref: Reference allele
        alt: Alternative allele(s)
        rsid: dbSNP ID (e.g., rs12345)
        maf: Minor allele frequency (0-1)
        variant_type: Type of variant
        info: Additional info from VCF
    """
    chrom: str
    pos: int
    ref: str
    alt: str
    rsid: Optional[str] = None
    maf: Optional[float] = None
    variant_type: VariantType = VariantType.SNP
    info: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Determine variant type based on ref/alt."""
        if len(self.ref) == 1 and len(self.alt) == 1:
            self.variant_type = VariantType.SNP
        elif len(self.ref) < len(self.alt):
            self.variant_type = VariantType.INSERTION
        elif len(self.ref) > len(self.alt):
            self.variant_type = VariantType.DELETION
        elif len(self.ref) > 1 and len(self.ref) == len(self.alt):
            self.variant_type = VariantType.MNP
        else:
            self.variant_type = VariantType.COMPLEX
    
    @property
    def end_pos(self) -> int:
        """End position of the variant."""
        return self.pos + len(self.ref) - 1
    
    def overlaps(self, start: int, end: int) -> bool:
        """Check if variant overlaps with a region."""
        return not (self.end_pos < start or self.pos > end)
    
    def __str__(self) -> str:
        rsid_str = f" ({self.rsid})" if self.rsid else ""
        return f"{self.chrom}:{self.pos} {self.ref}>{self.alt}{rsid_str}"


@dataclass
class VariantOverlap:
    """
    Represents an overlap between a primer and a variant.
    
    Attributes:
        variant: The overlapping variant
        primer_position: Position within the primer (0-based from 5')
        distance_from_3prime: Distance from 3' end
        impact: Impact level for primer function
    """
    variant: Variant
    primer_position: int
    distance_from_3prime: int
    impact: VariantImpact = VariantImpact.MEDIUM
    
    def __post_init__(self):
        """Determine impact based on position."""
        if self.distance_from_3prime <= 3:
            self.impact = VariantImpact.HIGH
        elif self.distance_from_3prime <= 6:
            self.impact = VariantImpact.MEDIUM
        else:
            self.impact = VariantImpact.LOW


@dataclass
class PrimerVariantResult:
    """
    Result of variant check for a single primer.
    
    Attributes:
        primer_id: Primer identifier
        primer_seq: Primer sequence
        primer_start: Genomic start position
        primer_end: Genomic end position
        strand: + or -
        overlaps: List of variant overlaps
        has_critical_variants: True if any HIGH impact variants
    """
    primer_id: str
    primer_seq: str
    primer_start: int
    primer_end: int
    strand: str = "+"
    overlaps: List[VariantOverlap] = field(default_factory=list)
    
    @property
    def has_critical_variants(self) -> bool:
        """Check if any HIGH impact variants."""
        return any(o.impact == VariantImpact.HIGH for o in self.overlaps)
    
    @property
    def variant_count(self) -> int:
        """Number of overlapping variants."""
        return len(self.overlaps)
    
    @property
    def high_impact_count(self) -> int:
        """Number of HIGH impact variants."""
        return sum(1 for o in self.overlaps if o.impact == VariantImpact.HIGH)


@dataclass
class PrimerPairVariantResult:
    """
    Result of variant check for a primer pair.
    
    Attributes:
        forward_result: Forward primer variant result
        reverse_result: Reverse primer variant result
        total_variants: Combined variant count
        has_critical_variants: True if any critical variants
    """
    forward_result: PrimerVariantResult
    reverse_result: PrimerVariantResult
    
    @property
    def total_variants(self) -> int:
        return self.forward_result.variant_count + self.reverse_result.variant_count
    
    @property
    def has_critical_variants(self) -> bool:
        return (self.forward_result.has_critical_variants or 
                self.reverse_result.has_critical_variants)
    
    @property
    def warnings(self) -> List[str]:
        """Generate warnings for critical variants."""
        warnings = []
        
        if self.forward_result.has_critical_variants:
            count = self.forward_result.high_impact_count
            warnings.append(f"Forward primer has {count} variant(s) near 3' end")
        
        if self.reverse_result.has_critical_variants:
            count = self.reverse_result.high_impact_count
            warnings.append(f"Reverse primer has {count} variant(s) near 3' end")
        
        return warnings
