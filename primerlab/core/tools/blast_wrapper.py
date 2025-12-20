"""
BLAST Wrapper (v0.3.0)

Wrapper for NCBI BLAST+ command-line tools.
Provides auto-detection, blastn queries, and database creation.
"""

import subprocess
import shutil
import tempfile
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

from primerlab.core.logger import get_logger
from primerlab.core.models.blast import BlastHit, BlastResult, AlignmentMethod

logger = get_logger()


# Default BLAST parameters
DEFAULT_BLAST_PARAMS = {
    "evalue": 10,           # E-value threshold
    "word_size": 7,         # Word size for short sequences (primers)
    "dust": "no",           # Don't filter low-complexity
    "max_target_seqs": 100, # Max number of hits
    "outfmt": 6,            # Tabular output format
    "task": "blastn-short", # Optimized for short queries
}


@dataclass
class BlastInstallation:
    """Information about BLAST+ installation."""
    available: bool
    blastn_path: Optional[str] = None
    makeblastdb_path: Optional[str] = None
    version: Optional[str] = None
    error: Optional[str] = None


class BlastWrapper:
    """
    Wrapper for NCBI BLAST+ command-line tools.
    
    v0.3.0: Provides primer-specific BLAST searches against custom databases.
    
    Attributes:
        params: BLAST search parameters
        installation: BLAST+ installation info
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize BLAST wrapper.
        
        Args:
            params: Custom BLAST parameters (merged with defaults)
        """
        self.params = {**DEFAULT_BLAST_PARAMS}
        if params:
            self.params.update(params)
        
        self._installation: Optional[BlastInstallation] = None
    
    @property
    def installation(self) -> BlastInstallation:
        """Get BLAST+ installation info (cached)."""
        if self._installation is None:
            self._installation = self._detect_blast()
        return self._installation
    
    @property
    def is_available(self) -> bool:
        """Check if BLAST+ is available."""
        return self.installation.available
    
    def _detect_blast(self) -> BlastInstallation:
        """
        Detect BLAST+ installation.
        
        Returns:
            BlastInstallation with paths and version info
        """
        # Try to find blastn
        blastn_path = shutil.which("blastn")
        makeblastdb_path = shutil.which("makeblastdb")
        
        if not blastn_path:
            return BlastInstallation(
                available=False,
                error="BLAST+ not found. Install from https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download"
            )
        
        # Get version
        version = None
        try:
            result = subprocess.run(
                [blastn_path, "-version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                # Parse version from output like "blastn: 2.12.0+"
                for line in result.stdout.split("\n"):
                    if "blastn:" in line:
                        version = line.split()[-1].strip()
                        break
        except Exception as e:
            logger.warning(f"Could not get BLAST version: {e}")
        
        logger.info(f"BLAST+ detected: {blastn_path} (version: {version or 'unknown'})")
        
        return BlastInstallation(
            available=True,
            blastn_path=blastn_path,
            makeblastdb_path=makeblastdb_path,
            version=version
        )
    
    def run_blastn(
        self,
        query_seq: str,
        database: str,
        query_id: str = "primer",
        params: Optional[Dict[str, Any]] = None
    ) -> BlastResult:
        """
        Run blastn search for a primer sequence.
        
        Args:
            query_seq: Primer sequence to search
            database: Path to BLAST database
            query_id: Identifier for the query
            params: Override default parameters
            
        Returns:
            BlastResult with hits
        """
        if not self.is_available:
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                method=AlignmentMethod.BLAST,
                success=False,
                error=self.installation.error
            )
        
        # Merge parameters
        search_params = {**self.params}
        if params:
            search_params.update(params)
        
        # Create temp file for query
        with tempfile.NamedTemporaryFile(mode='w', suffix='.fasta', delete=False) as f:
            f.write(f">{query_id}\n{query_seq}\n")
            query_file = f.name
        
        try:
            # Build command
            cmd = [
                self.installation.blastn_path,
                "-query", query_file,
                "-db", database,
                "-evalue", str(search_params["evalue"]),
                "-word_size", str(search_params["word_size"]),
                "-dust", search_params["dust"],
                "-max_target_seqs", str(search_params["max_target_seqs"]),
                "-outfmt", "6 sseqid stitle qstart qend sstart send pident length mismatch gaps evalue bitscore qseq sseq",
                "-task", search_params["task"]
            ]
            
            logger.debug(f"Running: {' '.join(cmd)}")
            
            # Run BLAST
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return BlastResult(
                    query_id=query_id,
                    query_seq=query_seq,
                    query_length=len(query_seq),
                    method=AlignmentMethod.BLAST,
                    database=database,
                    success=False,
                    error=f"BLAST failed: {result.stderr}"
                )
            
            # Parse results
            hits = self._parse_blast_output(result.stdout)
            
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                hits=hits,
                method=AlignmentMethod.BLAST,
                database=database,
                parameters=search_params,
                success=True
            )
            
        except subprocess.TimeoutExpired:
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                method=AlignmentMethod.BLAST,
                success=False,
                error="BLAST search timed out"
            )
        except Exception as e:
            return BlastResult(
                query_id=query_id,
                query_seq=query_seq,
                query_length=len(query_seq),
                method=AlignmentMethod.BLAST,
                success=False,
                error=f"BLAST error: {str(e)}"
            )
        finally:
            # Cleanup temp file
            try:
                os.unlink(query_file)
            except:
                pass
    
    def _parse_blast_output(self, output: str) -> List[BlastHit]:
        """
        Parse tabular BLAST output.
        
        Args:
            output: BLAST tabular output (outfmt 6)
            
        Returns:
            List of BlastHit objects
        """
        hits = []
        
        for line in output.strip().split("\n"):
            if not line:
                continue
            
            fields = line.split("\t")
            if len(fields) < 14:
                continue
            
            try:
                hit = BlastHit(
                    subject_id=fields[0],
                    subject_title=fields[1],
                    query_start=int(fields[2]),
                    query_end=int(fields[3]),
                    subject_start=int(fields[4]),
                    subject_end=int(fields[5]),
                    identity_percent=float(fields[6]),
                    alignment_length=int(fields[7]),
                    mismatches=int(fields[8]),
                    gaps=int(fields[9]),
                    evalue=float(fields[10]),
                    bit_score=float(fields[11]),
                    query_seq=fields[12] if len(fields) > 12 else "",
                    subject_seq=fields[13] if len(fields) > 13 else ""
                )
                hits.append(hit)
            except (ValueError, IndexError) as e:
                logger.warning(f"Could not parse BLAST hit: {line} ({e})")
                continue
        
        # Sort by bit score (best first)
        hits.sort(key=lambda h: -h.bit_score)
        
        return hits
    
    def make_database(
        self,
        fasta_path: str,
        db_name: Optional[str] = None,
        db_type: str = "nucl",
        title: Optional[str] = None
    ) -> bool:
        """
        Create BLAST database from FASTA file.
        
        Args:
            fasta_path: Path to input FASTA file
            db_name: Output database name (default: same as input)
            db_type: Database type ('nucl' or 'prot')
            title: Database title
            
        Returns:
            True if successful
        """
        if not self.is_available:
            logger.error("BLAST+ not available - cannot create database")
            return False
        
        if not self.installation.makeblastdb_path:
            logger.error("makeblastdb not found")
            return False
        
        fasta_path = Path(fasta_path)
        if not fasta_path.exists():
            logger.error(f"FASTA file not found: {fasta_path}")
            return False
        
        if db_name is None:
            db_name = str(fasta_path.with_suffix(""))
        
        if title is None:
            title = fasta_path.stem
        
        cmd = [
            self.installation.makeblastdb_path,
            "-in", str(fasta_path),
            "-dbtype", db_type,
            "-out", db_name,
            "-title", title
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info(f"Created BLAST database: {db_name}")
                return True
            else:
                logger.error(f"makeblastdb failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"makeblastdb error: {e}")
            return False


def check_blast_installation() -> BlastInstallation:
    """
    Quick check for BLAST+ installation.
    
    Returns:
        BlastInstallation with availability info
    """
    wrapper = BlastWrapper()
    return wrapper.installation
