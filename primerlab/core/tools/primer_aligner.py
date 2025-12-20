"""
Unified Primer Aligner (v0.3.0)

Unified interface for primer alignment using BLAST+ or Biopython fallback.
Automatically selects the best available method.
"""

from typing import Optional, Dict, Any, Tuple
from enum import Enum

from primerlab.core.logger import get_logger
from primerlab.core.models.blast import BlastResult, SpecificityResult, AlignmentMethod
from primerlab.core.tools.blast_wrapper import BlastWrapper, check_blast_installation
from primerlab.core.tools.align_fallback import BiopythonAligner, get_fallback_aligner

logger = get_logger()


class AlignmentMode(Enum):
    """Alignment method selection mode."""
    AUTO = "auto"           # Auto-select best available
    BLAST = "blast"         # Force BLAST+ (fail if not available)
    BIOPYTHON = "biopython" # Force Biopython fallback


class PrimerAligner:
    """
    Unified primer alignment interface.
    
    v0.3.0: Automatically selects BLAST+ if available, falls back to Biopython.
    
    Usage:
        aligner = PrimerAligner()
        result = aligner.search_primer("ATGCATGCATGC", "database.fasta")
    """
    
    def __init__(
        self,
        mode: AlignmentMode = AlignmentMode.AUTO,
        blast_params: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize primer aligner.
        
        Args:
            mode: Alignment method selection mode
            blast_params: Custom BLAST parameters
        """
        self.mode = mode
        self.blast_wrapper = BlastWrapper(blast_params)
        self.biopython_aligner = BiopythonAligner()
        
        # Determine active method
        self._active_method = self._select_method()
    
    def _select_method(self) -> AlignmentMethod:
        """Select alignment method based on mode and availability."""
        if self.mode == AlignmentMode.BLAST:
            if not self.blast_wrapper.is_available:
                raise RuntimeError(
                    "BLAST+ requested but not available. "
                    f"Error: {self.blast_wrapper.installation.error}"
                )
            return AlignmentMethod.BLAST
        
        elif self.mode == AlignmentMode.BIOPYTHON:
            if not self.biopython_aligner.is_available:
                raise RuntimeError("Biopython alignment requested but Biopython not installed")
            return AlignmentMethod.BIOPYTHON
        
        else:  # AUTO
            if self.blast_wrapper.is_available:
                logger.info("Using BLAST+ for alignment")
                return AlignmentMethod.BLAST
            elif self.biopython_aligner.is_available:
                logger.info("BLAST+ not available, using Biopython fallback")
                return AlignmentMethod.BIOPYTHON
            else:
                raise RuntimeError(
                    "No alignment method available. "
                    "Install BLAST+ or Biopython (pip install biopython)"
                )
    
    @property
    def active_method(self) -> AlignmentMethod:
        """Get the active alignment method."""
        return self._active_method
    
    @property
    def is_blast_available(self) -> bool:
        """Check if BLAST+ is available."""
        return self.blast_wrapper.is_available
    
    @property
    def is_biopython_available(self) -> bool:
        """Check if Biopython is available."""
        return self.biopython_aligner.is_available
    
    def search_primer(
        self,
        primer_seq: str,
        database: str,
        primer_id: str = "primer"
    ) -> BlastResult:
        """
        Search a primer against a database.
        
        Args:
            primer_seq: Primer sequence
            database: Path to database (FASTA or BLAST DB)
            primer_id: Identifier for the primer
            
        Returns:
            BlastResult with hits
        """
        if self._active_method == AlignmentMethod.BLAST:
            return self.blast_wrapper.run_blastn(
                query_seq=primer_seq,
                database=database,
                query_id=primer_id
            )
        else:
            return self.biopython_aligner.search_database(
                query_seq=primer_seq,
                database_path=database,
                query_id=primer_id
            )
    
    def check_primer_specificity(
        self,
        forward_primer: str,
        reverse_primer: str,
        database: str,
        target_id: Optional[str] = None
    ) -> SpecificityResult:
        """
        Check specificity of a primer pair against a database.
        
        Args:
            forward_primer: Forward primer sequence
            reverse_primer: Reverse primer sequence
            database: Path to database
            target_id: Expected target sequence ID (to mark as on-target)
            
        Returns:
            SpecificityResult with combined analysis
        """
        # Search forward primer
        fwd_result = self.search_primer(
            primer_seq=forward_primer,
            database=database,
            primer_id="forward"
        )
        
        # Search reverse primer
        rev_result = self.search_primer(
            primer_seq=reverse_primer,
            database=database,
            primer_id="reverse"
        )
        
        # Mark on-target hits if target_id provided
        if target_id:
            for hit in fwd_result.hits:
                if target_id in hit.subject_id or target_id in hit.subject_title:
                    hit.is_on_target = True
            for hit in rev_result.hits:
                if target_id in hit.subject_id or target_id in hit.subject_title:
                    hit.is_on_target = True
        
        return SpecificityResult(
            forward_result=fwd_result,
            reverse_result=rev_result
        )
    
    def make_blast_database(self, fasta_path: str, db_name: Optional[str] = None) -> bool:
        """
        Create BLAST database from FASTA file.
        
        Args:
            fasta_path: Path to FASTA file
            db_name: Output database name
            
        Returns:
            True if successful
        """
        if not self.blast_wrapper.is_available:
            logger.error("BLAST+ not available - cannot create database")
            return False
        
        return self.blast_wrapper.make_database(fasta_path, db_name)


def get_aligner(mode: str = "auto") -> PrimerAligner:
    """
    Get configured primer aligner.
    
    Args:
        mode: "auto", "blast", or "biopython"
        
    Returns:
        PrimerAligner instance
    """
    mode_enum = AlignmentMode(mode.lower())
    return PrimerAligner(mode=mode_enum)


def check_alignment_availability() -> Tuple[bool, bool, str]:
    """
    Check what alignment methods are available.
    
    Returns:
        Tuple of (blast_available, biopython_available, recommended_method)
    """
    blast_info = check_blast_installation()
    biopython_aligner = get_fallback_aligner()
    
    blast_available = blast_info.available
    biopython_available = biopython_aligner is not None
    
    if blast_available:
        recommended = "blast"
    elif biopython_available:
        recommended = "biopython"
    else:
        recommended = "none"
    
    return (blast_available, biopython_available, recommended)
