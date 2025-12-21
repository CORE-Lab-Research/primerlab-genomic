"""
NCBI Web BLAST Fallback (v0.3.2)

Fallback to NCBI BLAST web service when local BLAST+ is unavailable.
Uses Biopython's NCBIWWW module for web BLAST queries.
"""

import time
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from io import StringIO

logger = logging.getLogger(__name__)


@dataclass
class WebBlastResult:
    """Result from NCBI web BLAST."""
    query_id: str
    hits: List[Dict[str, Any]]
    search_time: float
    database: str
    program: str


class NCBIWebBlast:
    """
    NCBI Web BLAST client with rate limiting.
    
    Uses Biopython's NCBIWWW for web BLAST queries.
    Includes rate limiting to comply with NCBI guidelines.
    """
    
    # NCBI rate limit: 1 request per 3 seconds
    MIN_REQUEST_INTERVAL = 3.0
    
    def __init__(
        self,
        database: str = "nt",
        program: str = "blastn",
        timeout: int = 120,
        email: Optional[str] = None
    ):
        """
        Initialize NCBI Web BLAST client.
        
        Args:
            database: NCBI database (nt, nr, etc.)
            program: BLAST program (blastn, blastp, etc.)
            timeout: Request timeout in seconds
            email: Email for NCBI (recommended)
        """
        self.database = database
        self.program = program
        self.timeout = timeout
        self.email = email
        self._last_request_time = 0.0
        self._available = None
    
    def is_available(self) -> bool:
        """Check if Biopython NCBIWWW is available."""
        if self._available is None:
            try:
                from Bio.Blast import NCBIWWW
                self._available = True
            except ImportError:
                self._available = False
                logger.warning("Biopython not installed - NCBI web BLAST unavailable")
        return self._available
    
    def _rate_limit(self):
        """Apply rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.MIN_REQUEST_INTERVAL:
            sleep_time = self.MIN_REQUEST_INTERVAL - elapsed
            logger.debug(f"Rate limiting: sleeping {sleep_time:.1f}s")
            time.sleep(sleep_time)
        self._last_request_time = time.time()
    
    def blast(
        self,
        sequence: str,
        max_hits: int = 50,
        evalue: float = 10.0
    ) -> Optional[WebBlastResult]:
        """
        Run web BLAST query.
        
        Args:
            sequence: Query sequence
            max_hits: Maximum number of hits
            evalue: E-value threshold
            
        Returns:
            WebBlastResult or None if failed
        """
        if not self.is_available():
            logger.error("NCBI web BLAST not available")
            return None
        
        try:
            from Bio.Blast import NCBIWWW, NCBIXML
            
            self._rate_limit()
            
            logger.info(f"Running web BLAST against {self.database}...")
            start_time = time.time()
            
            # Run BLAST
            result_handle = NCBIWWW.qblast(
                program=self.program,
                database=self.database,
                sequence=sequence,
                hitlist_size=max_hits,
                expect=evalue,
                format_type="XML"
            )
            
            # Parse results
            blast_record = NCBIXML.read(result_handle)
            result_handle.close()
            
            search_time = time.time() - start_time
            logger.info(f"Web BLAST completed in {search_time:.1f}s")
            
            # Extract hits
            hits = []
            for alignment in blast_record.alignments:
                for hsp in alignment.hsps:
                    hits.append({
                        "subject_id": alignment.hit_id,
                        "subject_title": alignment.title[:100],
                        "identity": hsp.identities / hsp.align_length * 100,
                        "evalue": hsp.expect,
                        "score": hsp.score,
                        "query_start": hsp.query_start,
                        "query_end": hsp.query_end,
                        "subject_start": hsp.sbjct_start,
                        "subject_end": hsp.sbjct_end
                    })
            
            return WebBlastResult(
                query_id="query",
                hits=hits,
                search_time=search_time,
                database=self.database,
                program=self.program
            )
            
        except Exception as e:
            logger.error(f"Web BLAST failed: {e}")
            return None
    
    def blast_primers(
        self,
        forward: str,
        reverse: str,
        **kwargs
    ) -> Dict[str, Optional[WebBlastResult]]:
        """
        Run web BLAST for primer pair.
        
        Args:
            forward: Forward primer sequence
            reverse: Reverse primer sequence
            **kwargs: Additional BLAST parameters
            
        Returns:
            Dict with 'forward' and 'reverse' results
        """
        return {
            "forward": self.blast(forward, **kwargs),
            "reverse": self.blast(reverse, **kwargs)
        }


def check_ncbi_available() -> bool:
    """Check if NCBI web BLAST is available."""
    client = NCBIWebBlast()
    return client.is_available()
