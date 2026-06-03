"""
Off-target Finder (v0.3.0)

Finds all potential off-target binding sites for primers using BLAST or fallback.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from primerlab.core.logger import get_logger
from primerlab.core.models.blast import BlastHit, BlastResult, SpecificityResult, AlignmentMethod
from primerlab.core.tools.primer_aligner import PrimerAligner, AlignmentMode

logger = get_logger()


@dataclass
class OfftargetHit:
    """
    Represents a potential off-target binding site.
    
    Attributes:
        sequence_id: ID of the off-target sequence
        sequence_title: Description of the sequence
        position: Binding position on the sequence
        strand: '+' or '-' strand
        identity: Percent identity of the alignment
        mismatches: Number of mismatches
        gaps: Number of gaps
        evalue: E-value of the hit
        is_significant: Whether this is a significant off-target
        risk_level: 'high', 'medium', or 'low'
    """
    sequence_id: str
    sequence_title: str
    position: int
    strand: str
    identity: float
    mismatches: int
    gaps: int
    evalue: float
    is_significant: bool = True
    risk_level: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "sequence_id": self.sequence_id,
            "sequence_title": self.sequence_title,
            "position": self.position,
            "strand": self.strand,
            "identity": self.identity,
            "mismatches": self.mismatches,
            "gaps": self.gaps,
            "evalue": self.evalue,
            "is_significant": self.is_significant,
            "risk_level": self.risk_level
        }

    @classmethod
    def from_blast_hit(cls, hit: BlastHit) -> "OfftargetHit":
        """Create OfftargetHit from BlastHit."""
        # Determine risk level
        if hit.identity_percent >= 95 and hit.mismatches <= 1:
            risk = "high"
        elif hit.identity_percent >= 85:
            risk = "medium"
        else:
            risk = "low"

        return cls(
            sequence_id=hit.subject_id,
            sequence_title=hit.subject_title,
            position=hit.subject_start,
            strand="+" if hit.subject_start < hit.subject_end else "-",
            identity=hit.identity_percent,
            mismatches=hit.mismatches,
            gaps=hit.gaps,
            evalue=hit.evalue,
            is_significant=hit.is_significant(),
            risk_level=risk
        )


@dataclass
class OfftargetResult:
    """
    Complete off-target analysis result for a primer.
    
    Attributes:
        primer_id: Primer identifier
        primer_seq: Primer sequence
        target_id: Expected target sequence ID
        on_target_found: Whether on-target binding was found
        offtarget_count: Number of off-target hits
        significant_offtargets: Number of significant off-targets
        offtargets: List of off-target hits
        specificity_score: Overall specificity score (0-100)
        warnings: List of warning messages
    """
    primer_id: str
    primer_seq: str
    target_id: Optional[str] = None
    on_target_found: bool = False
    offtarget_count: int = 0
    significant_offtargets: int = 0
    offtargets: List[OfftargetHit] = field(default_factory=list)
    specificity_score: float = 100.0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "primer_id": self.primer_id,
            "primer_seq": self.primer_seq,
            "target_id": self.target_id,
            "on_target_found": self.on_target_found,
            "offtarget_count": self.offtarget_count,
            "significant_offtargets": self.significant_offtargets,
            "offtargets": [ot.to_dict() for ot in self.offtargets],
            "specificity_score": self.specificity_score,
            "warnings": self.warnings
        }


@dataclass
class PrimerPairOfftargetResult:
    """
    Combined off-target result for a primer pair.
    
    Attributes:
        forward_result: Off-target result for forward primer
        reverse_result: Off-target result for reverse primer
        probe_result: Off-target result for probe primer (optional)
        combined_score: Combined specificity score
        is_specific: True if both primers are specific
        potential_products: Number of potential off-target products
        warnings: Combined warnings
    """
    forward_result: OfftargetResult
    reverse_result: OfftargetResult
    probe_result: Optional[OfftargetResult] = None
    combined_score: float = 0.0
    is_specific: bool = True
    potential_products: int = 0
    warnings: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Calculate combined metrics."""
        scores = [self.forward_result.specificity_score, self.reverse_result.specificity_score]
        if self.probe_result:
            scores.append(self.probe_result.specificity_score)
        self.combined_score = sum(scores) / len(scores)

        # Check specificity
        if self.forward_result.specificity_score < 80:
            self.is_specific = False
        if self.reverse_result.specificity_score < 80:
            self.is_specific = False
        if self.probe_result and self.probe_result.specificity_score < 80:
            self.is_specific = False

        # Combine warnings
        self.warnings = (
            self.forward_result.warnings  +
            self.reverse_result.warnings
        )
        if self.probe_result:
            self.warnings.extend(self.probe_result.warnings)

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        data = {
            "forward_result": self.forward_result.to_dict(),
            "reverse_result": self.reverse_result.to_dict(),
            "combined_score": self.combined_score,
            "is_specific": self.is_specific,
            "potential_products": self.potential_products,
            "warnings": self.warnings
        }
        if self.probe_result:
            data["probe_result"] = self.probe_result.to_dict()
        return data


class OfftargetFinder:
    """
    Find off-target binding sites for primers.
    
    v0.3.0: Uses BLAST+ or Biopython fallback to search databases.
    
    Usage:
        finder = OfftargetFinder(database="genome.fasta")
        result = finder.find_offtargets("ATGCATGCATGC", target_id="gene_x")
    """

    # Default parameters for off-target detection
    DEFAULT_PARAMS = {
        "evalue_threshold": 10.0,       # E-value cutoff
        "identity_threshold": 70.0,     # Min identity % to report
        "max_offtargets": 50,           # Max off-targets to report
        "significant_identity": 85.0,   # Identity for "significant" hit
        "significant_evalue": 1e-3,     # E-value for "significant" hit
    }

    def __init__(
        self,
        database: str,
        target_id: Optional[str] = None,
        mode: str = "auto",
        params: Optional[Dict[str, Any]] = None,
        remote: bool = False
    ):
        """
        Initialize off-target finder.
        
        Args:
            database: Path to FASTA database or BLAST database
            target_id: Expected target sequence ID (to distinguish on-target)
            mode: Alignment mode ('auto', 'blast', 'biopython')
            params: Custom parameters
            remote: Force NCBI remote search
        """
        self.database = database
        self.target_id = target_id
        self.params = {**self.DEFAULT_PARAMS}
        if params:
            self.params.update(params)
        self.remote = remote

        # Initialize aligner
        mode_enum = AlignmentMode(mode.lower())
        self.aligner = PrimerAligner(mode=mode_enum, blast_params=self.params)

    def find_offtargets(
        self,
        primer_seq: str,
        primer_id: str = "primer",
        target_id: Optional[str] = None
    ) -> OfftargetResult:
        """
        Find off-target binding sites for a primer.
        
        Args:
            primer_seq: Primer sequence
            primer_id: Primer identifier
            target_id: Override target ID for this search
            
        Returns:
            OfftargetResult with all off-target hits
        """
        target = target_id or self.target_id

        # Search database
        blast_result = self.aligner.search_primer(
            primer_seq=primer_seq,
            database=self.database,
            primer_id=primer_id,
            remote=self.remote
        )

        if not blast_result.success:
            return OfftargetResult(
                primer_id=primer_id,
                primer_seq=primer_seq,
                target_id=target,
                warnings=[f"Search failed: {blast_result.error}"]
            )

        # Process hits
        offtargets = []
        on_target_found = False

        for hit in blast_result.hits:
            # Check if this is the on-target hit
            is_on_target = False
            if target:
                if target in hit.subject_id or target in hit.subject_title:
                    is_on_target = True
                    on_target_found = True
                    hit.is_on_target = True

            # Skip on-target hits
            if is_on_target:
                continue

            # Filter by identity
            if hit.identity_percent < self.params["identity_threshold"]:
                continue

            # Create off-target hit
            offtarget = OfftargetHit.from_blast_hit(hit)
            offtargets.append(offtarget)

        # Limit results
        offtargets = offtargets[:self.params["max_offtargets"]]

        # Count significant off-targets
        significant = sum(1 for ot in offtargets if ot.is_significant)

        # Calculate specificity score
        specificity = self._calculate_specificity(offtargets)

        # Generate warnings
        warnings = []
        if not on_target_found and target:
            warnings.append(f"Expected target '{target}' not found in database")
        if significant > 5:
            warnings.append(f"High off-target risk: {significant} significant off-targets")
        elif significant > 0:
            warnings.append(f"{significant} potential off-target site(s) found")

        return OfftargetResult(
            primer_id=primer_id,
            primer_seq=primer_seq,
            target_id=target,
            on_target_found=on_target_found,
            offtarget_count=len(offtargets),
            significant_offtargets=significant,
            offtargets=offtargets,
            specificity_score=specificity,
            warnings=warnings
        )

    def find_primer_pair_offtargets(
        self,
        forward_primer: str,
        reverse_primer: str,
        probe_primer: Optional[str] = None,
        target_id: Optional[str] = None
    ) -> PrimerPairOfftargetResult:
        """
        Find off-targets for both primers (and optional probe) in a pair.
        
        Args:
            forward_primer: Forward primer sequence
            reverse_primer: Reverse primer sequence
            probe_primer: Probe primer sequence (optional)
            target_id: Target sequence ID
            
        Returns:
            PrimerPairOfftargetResult with combined analysis
        """
        fwd_result = self.find_offtargets(
            primer_seq=forward_primer,
            primer_id="forward",
            target_id=target_id
        )

        rev_result = self.find_offtargets(
            primer_seq=reverse_primer,
            primer_id="reverse",
            target_id=target_id
        )

        probe_result = None
        if probe_primer:
            probe_result = self.find_offtargets(
                primer_seq=probe_primer,
                primer_id="probe",
                target_id=target_id
            )

        # Calculate potential off-target products
        # (where both primers could bind to same sequence)
        potential_products = self._count_potential_products(fwd_result, rev_result)

        result = PrimerPairOfftargetResult(
            forward_result=fwd_result,
            reverse_result=rev_result,
            probe_result=probe_result,
            potential_products=potential_products
        )

        if potential_products > 0:
            result.warnings.append(
                f"Warning: {potential_products} potential off-target product(s)"
            )

        return result

    def _calculate_specificity(self, offtargets: List[OfftargetHit]) -> float:
        """
        Calculate specificity score based on off-targets.
        
        100 = No off-targets
        0 = Many high-identity off-targets
        """
        if not offtargets:
            return 100.0

        penalty = 0.0
        for ot in offtargets:
            if ot.risk_level == "high":
                penalty += 15.0
            elif ot.risk_level == "medium":
                penalty += 8.0
            else:
                penalty += 3.0

        score = max(0.0, 100.0 - penalty)
        return round(score, 1)

    def _count_potential_products(
        self,
        fwd_result: OfftargetResult,
        rev_result: OfftargetResult
    ) -> int:
        """
        Count potential off-target products.
        
        Products form when both primers bind to the same sequence.
        """
        fwd_seqs = {ot.sequence_id for ot in fwd_result.offtargets}
        rev_seqs = {ot.sequence_id for ot in rev_result.offtargets}

        # Sequences where both primers could bind
        common = fwd_seqs & rev_seqs
        return len(common)


def find_offtargets(
    primer_seq: str,
    database: str,
    target_id: Optional[str] = None,
    mode: str = "auto"
) -> OfftargetResult:
    """
    Convenience function to find off-targets.
    
    Args:
        primer_seq: Primer sequence
        database: Path to database
        target_id: Expected target ID
        mode: Alignment mode
        
    Returns:
        OfftargetResult
    """
    finder = OfftargetFinder(database=database, target_id=target_id, mode=mode)
    return finder.find_offtargets(primer_seq)
