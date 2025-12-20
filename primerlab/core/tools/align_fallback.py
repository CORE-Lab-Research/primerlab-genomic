"""
Biopython Alignment Fallback (v0.3.0)

Fallback alignment using Biopython's PairwiseAligner
when BLAST+ is not available.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from primerlab.core.logger import get_logger
from primerlab.core.models.blast import BlastHit, BlastResult, AlignmentMethod

logger = get_logger()

# Try to import Biopython
try:
    from Bio import Align
    from Bio.Seq import Seq
    BIOPYTHON_AVAILABLE = True
except ImportError:
    BIOPYTHON_AVAILABLE = False
    logger.warning("Biopython not available - fallback alignment disabled")


@dataclass
class AlignmentConfig:
    """Configuration for pairwise alignment."""
    match_score: float = 2.0
    mismatch_score: float = -1.0
    open_gap_score: float = -2.0
    extend_gap_score: float = -0.5
    min_score_threshold: float = 15.0  # Minimum alignment score
    min_identity_percent: float = 70.0  # Minimum identity


class BiopythonAligner:
    """
    Fallback aligner using Biopython's PairwiseAligner.
    
    v0.3.0: Use when BLAST+ is not installed.
    Works well for small databases and primer sequences.
    """
    
    def __init__(self, config: Optional[AlignmentConfig] = None):
        """
        Initialize aligner.
        
        Args:
            config: Alignment configuration
        """
        self.config = config or AlignmentConfig()
        self._aligner = None
    
    @property
    def is_available(self) -> bool:
        """Check if Biopython is available."""
        return BIOPYTHON_AVAILABLE
    
    @property
    def aligner(self):
        """Get or create PairwiseAligner instance."""
        if self._aligner is None and BIOPYTHON_AVAILABLE:
            self._aligner = Align.PairwiseAligner()
            self._aligner.mode = 'local'  # Smith-Waterman local alignment
            self._aligner.match_score = self.config.match_score
            self._aligner.mismatch_score = self.config.mismatch_score
            self._aligner.open_gap_score = self.config.open_gap_score
            self._aligner.extend_gap_score = self.config.extend_gap_score
        return self._aligner
    
    def search_database(
        self,
        query_seq: str,
        database_path: str,
        query_id: str = "primer"
    ) -> BlastResult:
        """
        Search a FASTA database using pairwise alignment.
        
        Args:
            query_seq: Primer sequence to search
            database_path: Path to FASTA database file
            query_id: Identifier for the query
            
        Returns:
            BlastResult with hits
        """
        if not self.is_available:
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                method=AlignmentMethod.BIOPYTHON,
                success=False,
                error="Biopython not available"
            )
        
        try:
            # Load database sequences
            sequences = self._load_fasta(database_path)
            
            if not sequences:
                return BlastResult(
                    query_id=query_id,
                    query_seq=query_seq,
                    query_length=len(query_seq),
                    method=AlignmentMethod.BIOPYTHON,
                    success=False,
                    error=f"No sequences found in {database_path}"
                )
            
            # Align query against each sequence
            hits = []
            for seq_id, seq_title, seq_data in sequences:
                hit = self._align_to_sequence(
                    query_seq=query_seq,
                    subject_seq=seq_data,
                    subject_id=seq_id,
                    subject_title=seq_title
                )
                if hit:
                    hits.append(hit)
            
            # Sort by score
            hits.sort(key=lambda h: -h.bit_score)
            
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                hits=hits,
                method=AlignmentMethod.BIOPYTHON,
                database=database_path,
                success=True
            )
            
        except Exception as e:
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                method=AlignmentMethod.BIOPYTHON,
                success=False,
                error=f"Alignment error: {str(e)}"
            )
    
    def _load_fasta(self, path: str) -> List[tuple]:
        """
        Load sequences from FASTA file.
        
        Returns:
            List of (id, title, sequence) tuples
        """
        sequences = []
        current_id = ""
        current_title = ""
        current_seq = []
        
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    # Save previous sequence
                    if current_id and current_seq:
                        sequences.append((current_id, current_title, ''.join(current_seq)))
                    
                    # Parse header
                    header = line[1:].split(None, 1)
                    current_id = header[0] if header else "unknown"
                    current_title = header[1] if len(header) > 1 else ""
                    current_seq = []
                else:
                    current_seq.append(line.upper())
            
            # Don't forget last sequence
            if current_id and current_seq:
                sequences.append((current_id, current_title, ''.join(current_seq)))
        
        return sequences
    
    def _align_to_sequence(
        self,
        query_seq: str,
        subject_seq: str,
        subject_id: str,
        subject_title: str
    ) -> Optional[BlastHit]:
        """
        Align query to a single subject sequence.
        
        Returns:
            BlastHit if alignment meets thresholds, None otherwise
        """
        if not self.aligner:
            return None
        
        try:
            # Perform alignment
            alignments = self.aligner.align(query_seq.upper(), subject_seq.upper())
            
            if not alignments:
                return None
            
            # Get best alignment
            best = alignments[0]
            score = best.score
            
            # Check threshold
            if score < self.config.min_score_threshold:
                return None
            
            # Calculate alignment statistics
            aligned_query, aligned_subject = self._get_aligned_sequences(best)
            
            matches = 0
            mismatches = 0
            gaps = 0
            
            for q, s in zip(aligned_query, aligned_subject):
                if q == '-' or s == '-':
                    gaps += 1
                elif q == s:
                    matches += 1
                else:
                    mismatches += 1
            
            alignment_length = len(aligned_query)
            identity_percent = (matches / alignment_length * 100) if alignment_length > 0 else 0
            
            # Check identity threshold
            if identity_percent < self.config.min_identity_percent:
                return None
            
            # Get alignment coordinates
            query_start, query_end, subject_start, subject_end = self._get_coordinates(best)
            
            return BlastHit(
                subject_id=subject_id,
                subject_title=subject_title,
                query_start=query_start + 1,  # 1-indexed
                query_end=query_end,
                subject_start=subject_start + 1,  # 1-indexed
                subject_end=subject_end,
                identity_percent=round(identity_percent, 1),
                alignment_length=alignment_length,
                mismatches=mismatches,
                gaps=gaps,
                evalue=self._score_to_evalue(score, len(query_seq)),  # Approximate
                bit_score=score,  # Using raw score
                query_seq=aligned_query,
                subject_seq=aligned_subject
            )
            
        except Exception as e:
            logger.debug(f"Alignment failed for {subject_id}: {e}")
            return None
    
    def _get_aligned_sequences(self, alignment) -> tuple:
        """Extract aligned sequence strings from alignment object."""
        try:
            # Format as string and parse
            alignment_str = str(alignment)
            lines = alignment_str.split('\n')
            
            query_aligned = ""
            subject_aligned = ""
            
            for i, line in enumerate(lines):
                if line.startswith("target"):
                    subject_aligned = line.split()[-1] if line.split() else ""
                elif line.startswith("query"):
                    query_aligned = line.split()[-1] if line.split() else ""
            
            if not query_aligned or not subject_aligned:
                # Fallback: use alignment directly if available
                return (str(alignment.query), str(alignment.target))
            
            return (query_aligned, subject_aligned)
        except:
            return ("", "")
    
    def _get_coordinates(self, alignment) -> tuple:
        """Get alignment coordinates (start, end for query and subject)."""
        try:
            # Get coordinates from alignment object
            coords = alignment.coordinates
            if coords is not None and len(coords) == 2:
                query_coords = coords[0]
                subject_coords = coords[1]
                
                query_start = min(query_coords)
                query_end = max(query_coords)
                subject_start = min(subject_coords)
                subject_end = max(subject_coords)
                
                return (query_start, query_end, subject_start, subject_end)
        except:
            pass
        
        return (0, 0, 0, 0)
    
    def _score_to_evalue(self, score: float, query_len: int) -> float:
        """
        Approximate e-value from alignment score.
        
        This is a rough estimate - BLAST calculates this more accurately.
        """
        if score <= 0:
            return 1000.0
        
        # Rough approximation based on score
        # Higher score = lower e-value
        evalue = 10 ** (-(score - query_len) / 10)
        return min(max(evalue, 1e-100), 1000.0)


def get_fallback_aligner() -> Optional[BiopythonAligner]:
    """
    Get Biopython aligner if available.
    
    Returns:
        BiopythonAligner or None if not available
    """
    aligner = BiopythonAligner()
    return aligner if aligner.is_available else None
