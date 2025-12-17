"""
PrimerLab Primer Database Module

v0.1.5 Priority 6: SQLite-based storage for primer design history.

Features:
- Store successful primer designs locally
- Search previous designs by gene/sequence
- Track design metadata (params, quality scores)
- Export history to CSV
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from primerlab.core.logger import get_logger

logger = get_logger()

# Default database path
DEFAULT_DB_PATH = Path.home() / ".primerlab" / "primer_history.db"


class PrimerDatabase:
    """
    SQLite database for storing primer design history.
    
    Usage:
        db = PrimerDatabase()
        db.save_design(result, config)
        history = db.search(gene="GAPDH")
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file (default: ~/.primerlab/primer_history.db)
        """
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS designs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                gene_name TEXT,
                workflow TEXT NOT NULL,
                
                -- Forward primer
                fwd_sequence TEXT,
                fwd_tm REAL,
                fwd_gc REAL,
                fwd_length INTEGER,
                
                -- Reverse primer
                rev_sequence TEXT,
                rev_tm REAL,
                rev_gc REAL,
                rev_length INTEGER,
                
                -- Probe (qPCR)
                probe_sequence TEXT,
                probe_tm REAL,
                
                -- Amplicon
                amplicon_length INTEGER,
                amplicon_gc REAL,
                
                -- Quality
                quality_score REAL,
                quality_category TEXT,
                
                -- Serialized data
                config_json TEXT,
                result_json TEXT,
                
                -- Metadata
                notes TEXT
            )
        """)
        
        # Index for common searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_gene_name ON designs(gene_name)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fwd_sequence ON designs(fwd_sequence)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON designs(created_at)
        """)
        
        self.conn.commit()
        logger.debug(f"Database initialized: {self.db_path}")
    
    def save_design(
        self, 
        result: Dict[str, Any], 
        config: Optional[Dict[str, Any]] = None,
        gene_name: Optional[str] = None,
        notes: Optional[str] = None
    ) -> int:
        """
        Save a primer design to the database.
        
        Args:
            result: WorkflowResult as dict
            config: Configuration used for design
            gene_name: Optional gene name (extracted from result if not provided)
            notes: Optional notes about the design
            
        Returns:
            ID of the saved record
        """
        primers = result.get("primers", {})
        amplicons = result.get("amplicons", [])
        qc = result.get("qc", {})
        metadata = result.get("metadata", {})
        
        # Extract gene name
        if not gene_name:
            gene_name = metadata.get("sequence_name") or metadata.get("gene_name") or "unknown"
        
        # Forward primer
        fwd = primers.get("forward", {})
        fwd_seq = fwd.get("sequence", "")
        fwd_tm = fwd.get("tm", 0)
        fwd_gc = fwd.get("gc", 0)
        fwd_len = fwd.get("length", len(fwd_seq) if fwd_seq else 0)
        
        # Reverse primer
        rev = primers.get("reverse", {})
        rev_seq = rev.get("sequence", "")
        rev_tm = rev.get("tm", 0)
        rev_gc = rev.get("gc", 0)
        rev_len = rev.get("length", len(rev_seq) if rev_seq else 0)
        
        # Probe
        probe = primers.get("probe", {})
        probe_seq = probe.get("sequence", "")
        probe_tm = probe.get("tm", 0)
        
        # Amplicon
        amp = amplicons[0] if amplicons else {}
        amp_len = amp.get("length", 0)
        amp_gc = amp.get("gc", 0)
        
        # Quality
        quality_score = qc.get("quality_score", 0)
        quality_category = qc.get("quality_category", "N/A")
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO designs (
                created_at, gene_name, workflow,
                fwd_sequence, fwd_tm, fwd_gc, fwd_length,
                rev_sequence, rev_tm, rev_gc, rev_length,
                probe_sequence, probe_tm,
                amplicon_length, amplicon_gc,
                quality_score, quality_category,
                config_json, result_json, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            gene_name,
            result.get("workflow", "pcr"),
            fwd_seq, fwd_tm, fwd_gc, fwd_len,
            rev_seq, rev_tm, rev_gc, rev_len,
            probe_seq if probe_seq else None, probe_tm if probe_seq else None,
            amp_len, amp_gc,
            quality_score, quality_category,
            json.dumps(config) if config else None,
            json.dumps(result),
            notes
        ))
        
        self.conn.commit()
        record_id = cursor.lastrowid
        logger.info(f"Saved design to database: ID={record_id}, gene={gene_name}")
        return record_id
    
    def search(
        self,
        gene: Optional[str] = None,
        sequence: Optional[str] = None,
        workflow: Optional[str] = None,
        min_quality: Optional[float] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search primer history.
        
        Args:
            gene: Filter by gene name (partial match)
            sequence: Filter by primer sequence (exact match)
            workflow: Filter by workflow type
            min_quality: Minimum quality score
            limit: Max results to return
            
        Returns:
            List of matching design records
        """
        conditions = []
        params = []
        
        if gene:
            conditions.append("gene_name LIKE ?")
            params.append(f"%{gene}%")
        
        if sequence:
            conditions.append("(fwd_sequence = ? OR rev_sequence = ?)")
            params.extend([sequence.upper(), sequence.upper()])
        
        if workflow:
            conditions.append("workflow = ?")
            params.append(workflow.lower())
        
        if min_quality:
            conditions.append("quality_score >= ?")
            params.append(min_quality)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor = self.conn.cursor()
        cursor.execute(f"""
            SELECT * FROM designs
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        """, params + [limit])
        
        results = []
        for row in cursor.fetchall():
            results.append(dict(row))
        
        return results
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific design by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM designs WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def delete(self, record_id: int) -> bool:
        """Delete a design by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM designs WHERE id = ?", (record_id,))
        self.conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted design: ID={record_id}")
        return deleted
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent designs."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, created_at, gene_name, workflow, quality_score, quality_category,
                   fwd_sequence, rev_sequence, amplicon_length
            FROM designs
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM designs")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT workflow, COUNT(*) as count
            FROM designs
            GROUP BY workflow
        """)
        by_workflow = {row[0]: row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT AVG(quality_score) FROM designs")
        avg_quality = cursor.fetchone()[0] or 0
        
        return {
            "total_designs": total,
            "by_workflow": by_workflow,
            "avg_quality_score": round(avg_quality, 1)
        }
    
    def export_csv(self, output_path: str) -> str:
        """Export all designs to CSV."""
        import csv
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, created_at, gene_name, workflow,
                   fwd_sequence, fwd_tm, fwd_gc,
                   rev_sequence, rev_tm, rev_gc,
                   probe_sequence, amplicon_length, amplicon_gc,
                   quality_score, quality_category
            FROM designs
            ORDER BY created_at DESC
        """)
        
        path = Path(output_path)
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Date", "Gene", "Workflow",
                "Fwd Sequence", "Fwd Tm", "Fwd GC%",
                "Rev Sequence", "Rev Tm", "Rev GC%",
                "Probe Sequence", "Amplicon Length", "Amplicon GC%",
                "Quality Score", "Quality Category"
            ])
            
            for row in cursor.fetchall():
                writer.writerow(row)
        
        logger.info(f"Exported {cursor.rowcount} designs to: {path}")
        return str(path)
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def format_history_table(designs: List[Dict[str, Any]]) -> str:
    """Format designs as CLI table."""
    if not designs:
        return "No designs found."
    
    lines = []
    lines.append("")
    lines.append("=" * 90)
    lines.append(f"{'ID':<6} {'Date':<12} {'Gene':<15} {'Type':<6} {'Fwd Primer':<20} {'QS':>6}")
    lines.append("-" * 90)
    
    for d in designs:
        date_str = d.get("created_at", "")[:10]
        gene = (d.get("gene_name") or "?")[:15]
        workflow = (d.get("workflow") or "?")[:6]
        fwd_seq = (d.get("fwd_sequence") or "?")[:20]
        qs = d.get("quality_score") or 0
        
        lines.append(f"{d['id']:<6} {date_str:<12} {gene:<15} {workflow:<6} {fwd_seq:<20} {qs:>6.1f}")
    
    lines.append("=" * 90)
    lines.append(f"Total: {len(designs)} designs")
    lines.append("")
    
    return "\n".join(lines)
