"""
Async Remote BLAST Wrapper (v1.3.0)

Handles end-to-end off-target checking against NCBI databases
using the local BLAST+ CLI with the `-remote` flag asynchronously.
Prevents the need to download massive local databases and speeds up execution
using asyncio for batch processing.
"""

import asyncio
import os
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from primerlab.core.logger import get_logger
from primerlab.core.models.blast import BlastHit, BlastResult, AlignmentMethod

logger = get_logger()

class AsyncRemoteBlast:
    """
    Asynchronous wrapper for NCBI remote BLAST execution using `blastn -remote`.
    """
    def __init__(self, database: str = "nt", api_key: Optional[str] = None):
        """
        Initialize the async BLAST engine.
        
        Args:
            database: Target NCBI database (e.g., 'nt', 'refseq_rna').
            api_key: NCBI API Key to boost concurrency from 3 to 10 req/sec.
        """
        self.database = database
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        
        # NCBI limits: 3/sec without key, 10/sec with key
        limit = 10 if self.api_key else 3
        self.semaphore = asyncio.Semaphore(limit)
        
        if self.api_key:
            logger.info(f"Initialized AsyncRemoteBlast with NCBI API Key (limit: {limit} concurrent jobs)")
        else:
            logger.info(f"Initialized AsyncRemoteBlast WITHOUT API Key (limit: {limit} concurrent jobs). Set NCBI_API_KEY for faster processing.")

    async def _run_single_blast(
        self, 
        query_id: str, 
        query_seq: str, 
        params: Dict[str, Any]
    ) -> BlastResult:
        """Run a single BLAST query asynchronously using the semaphore."""
        async with self.semaphore:
            # Create a temporary fasta file for the query
            fd, temp_path = tempfile.mkstemp(suffix=".fasta")
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(f">{query_id}\n{query_seq}\n")
                
                # Build CLI arguments
                cmd = [
                    "blastn",
                    "-query", temp_path,
                    "-db", self.database,
                    "-remote",
                    "-outfmt", "6 sseqid stitle qstart qend sstart send pident length mismatch gaps evalue bitscore qseq sseq",
                    "-max_target_seqs", str(params.get("max_target_seqs", 50)),
                    "-evalue", str(params.get("evalue", 10)),
                    "-word_size", str(params.get("word_size", 7)),
                    "-dust", "no"
                ]
                
                env = os.environ.copy()
                if self.api_key:
                    env["NCBI_API_KEY"] = self.api_key

                import time
                start_time = time.time()
                logger.info(f"[{query_id}] Dispatched remote BLAST query to NCBI. Target database: {self.database}")
                
                # Spawn process
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env
                )
                
                # Heartbeat logging task to keep the user informed
                async def heartbeat():
                    try:
                        while True:
                            await asyncio.sleep(10)
                            elapsed = int(time.time() - start_time)
                            logger.info(f"[{query_id}] Remote BLAST still running... ({elapsed}s elapsed)")
                    except asyncio.CancelledError:
                        pass
                
                heartbeat_task = asyncio.create_task(heartbeat())
                try:
                    stdout, stderr = await process.communicate()
                finally:
                    heartbeat_task.cancel()
                
                elapsed = int(time.time() - start_time)
                if process.returncode != 0:
                    logger.error(f"[{query_id}] BLAST failed in {elapsed}s: {stderr.decode()}")
                    return BlastResult(
                        query_id=query_id,
                        query_seq=query_seq,
                        query_length=len(query_seq),
                        method=AlignmentMethod.BLAST,
                        database=self.database,
                        success=False,
                        error=stderr.decode()
                    )
                    
                hits = self._parse_tabular_output(stdout.decode())
                logger.info(f"[{query_id}] BLAST completed successfully in {elapsed}s. Found {len(hits)} hits.")
                
                return BlastResult(
                    query_id=query_id,
                    query_seq=query_seq,
                    query_length=len(query_seq),
                    hits=hits,
                    method=AlignmentMethod.BLAST,
                    database=self.database,
                    parameters=params,
                    success=True
                )
            except Exception as e:
                logger.error(f"[{query_id}] Async BLAST exception: {e}")
                return BlastResult(
                    query_id=query_id,
                    query_seq=query_seq,
                    query_length=len(query_seq),
                    method=AlignmentMethod.BLAST,
                    success=False,
                    error=str(e)
                )
            finally:
                # Always cleanup the temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    def _parse_tabular_output(self, output: str) -> List[BlastHit]:
        """Parse the tabular output from blastn (-outfmt 6)."""
        hits = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            fields = line.split("\t")
            if len(fields) < 12:
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
                logger.warning(f"Failed to parse BLAST hit row: {e}")
        
        hits.sort(key=lambda h: -h.bit_score)
        return hits

    async def batch_blast(self, queries: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> Dict[str, BlastResult]:
        """
        Execute multiple BLAST queries concurrently.
        
        Args:
            queries: Dictionary mapping query_id -> query sequence
            params: Optional BLAST parameters (evalue, max_target_seqs, etc)
            
        Returns:
            Dictionary mapping query_id -> BlastResult
        """
        params = params or {}
        tasks = []
        
        logger.info(f"Dispatching {len(queries)} asynchronous remote BLAST tasks...")
        
        for q_id, seq in queries.items():
            tasks.append(self._run_single_blast(q_id, seq, params))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = {}
        for (q_id, _), res in zip(queries.items(), results):
            if isinstance(res, Exception):
                logger.error(f"[{q_id}] Unhandled Exception: {res}")
                final_results[q_id] = BlastResult(
                    query_id=q_id,
                    query_seq=queries[q_id],
                    query_length=len(queries[q_id]),
                    method=AlignmentMethod.BLAST,
                    success=False,
                    error=str(res)
                )
            else:
                final_results[q_id] = res
                
        return final_results
