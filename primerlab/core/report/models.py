"""
Report Data Models (v0.3.3)

Dataclasses for primer report generation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class ReportFormat(Enum):
    """Supported report formats."""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"


@dataclass
class PrimerInfo:
    """Individual primer information."""
    name: str
    sequence: str
    length: int
    tm: float
    gc_percent: float
    position: Optional[int] = None
    orientation: str = "forward"  # forward or reverse


@dataclass
class DesignSummary:
    """Summary of primer design results."""
    forward_primer: Optional[PrimerInfo] = None
    reverse_primer: Optional[PrimerInfo] = None
    probe: Optional[PrimerInfo] = None
    product_size: Optional[int] = None
    design_method: str = "primer3"
    candidates_evaluated: int = 0
    quality_score: float = 0.0
    
    @property
    def has_primers(self) -> bool:
        return self.forward_primer is not None and self.reverse_primer is not None


@dataclass
class ValidationSummary:
    """Summary of in-silico validation results."""
    validated: bool = False
    amplicons_predicted: int = 0
    primary_product_size: Optional[int] = None
    off_products: int = 0
    forward_binding_score: float = 0.0
    reverse_binding_score: float = 0.0
    pcr_success_probability: float = 0.0
    warnings: List[str] = field(default_factory=list)


@dataclass
class OfftargetSummary:
    """Summary of off-target analysis results."""
    checked: bool = False
    database: str = ""
    forward_hits: int = 0
    reverse_hits: int = 0
    forward_grade: str = "?"  # A-F
    reverse_grade: str = "?"
    combined_grade: str = "?"
    specificity_score: float = 0.0
    high_risk_sites: int = 0
    alignment_method: str = "auto"


@dataclass
class VariantSummary:
    """Summary of variant/SNP analysis."""
    checked: bool = False
    vcf_file: str = ""
    forward_overlaps: int = 0
    reverse_overlaps: int = 0
    critical_variants: int = 0  # 3' end overlaps
    maf_threshold: Optional[float] = None


@dataclass
class PrimerReport:
    """
    Complete primer report combining all analyses.
    
    This is the main report dataclass that aggregates:
    - Design results
    - Validation results  
    - Off-target analysis
    - Variant check
    """
    # Metadata
    report_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    primerlab_version: str = ""
    config_file: Optional[str] = None
    sequence_source: str = ""
    
    # Summaries
    design: DesignSummary = field(default_factory=DesignSummary)
    validation: ValidationSummary = field(default_factory=ValidationSummary)
    offtarget: OfftargetSummary = field(default_factory=OfftargetSummary)
    variant: VariantSummary = field(default_factory=VariantSummary)
    
    # Overall Status
    overall_grade: str = "?"  # A-F
    overall_score: float = 0.0
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    def calculate_overall_grade(self) -> str:
        """Calculate overall grade from all analyses."""
        scores = []
        
        # Design score
        if self.design.has_primers:
            scores.append(self.design.quality_score)
        
        # Validation score
        if self.validation.validated:
            scores.append(self.validation.pcr_success_probability * 100)
        
        # Offtarget score
        if self.offtarget.checked:
            scores.append(self.offtarget.specificity_score)
        
        if not scores:
            return "?"
        
        avg_score = sum(scores) / len(scores)
        self.overall_score = avg_score
        
        if avg_score >= 90:
            self.overall_grade = "A"
        elif avg_score >= 80:
            self.overall_grade = "B"
        elif avg_score >= 70:
            self.overall_grade = "C"
        elif avg_score >= 60:
            self.overall_grade = "D"
        else:
            self.overall_grade = "F"
        
        return self.overall_grade
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        from dataclasses import asdict
        return asdict(self)
