"""
Alignment Cache for Species-Check.

SQLite-based caching to speed up repeated alignment operations.
"""

import hashlib
import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AlignmentCache:
    """
    SQLite-based cache for alignment results.
    
    Cache key: hash(primer_seq + template_seq)
    TTL: configurable, default 7 days
    """
    
    def __init__(
        self,
        cache_path: Optional[str] = None,
        ttl_days: int = 7
    ):
        """
        Initialize cache.
        
        Args:
            cache_path: Path to SQLite database. Default: ~/.primerlab/cache.db
            ttl_days: Time-to-live for cache entries
        """
        if cache_path is None:
            cache_dir = Path.home() / ".primerlab"
            cache_dir.mkdir(exist_ok=True)
            cache_path = str(cache_dir / "species_cache.db")
        
        self.cache_path = cache_path
        self.ttl_days = ttl_days
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alignment_cache (
                cache_key TEXT PRIMARY KEY,
                primer_name TEXT,
                species_name TEXT,
                result_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index on created_at for TTL cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON alignment_cache(created_at)
        """)
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Cache initialized at {self.cache_path}")
    
    def _make_key(self, primer_seq: str, template_seq: str) -> str:
        """Generate cache key from sequences."""
        combined = f"{primer_seq.upper()}:{template_seq.upper()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def get(
        self,
        primer_seq: str,
        template_seq: str,
        primer_name: str = "",
        species_name: str = ""
    ) -> Optional[Dict]:
        """
        Get cached alignment result.
        
        Returns:
            Cached result dict or None if not found/expired
        """
        cache_key = self._make_key(primer_seq, template_seq)
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT result_json, created_at 
            FROM alignment_cache 
            WHERE cache_key = ?
        """, (cache_key,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return None
        
        result_json, created_at = row
        
        # Check TTL
        created = datetime.fromisoformat(created_at)
        if datetime.now() - created > timedelta(days=self.ttl_days):
            self.delete(primer_seq, template_seq)
            return None
        
        return json.loads(result_json)
    
    def set(
        self,
        primer_seq: str,
        template_seq: str,
        result: Dict,
        primer_name: str = "",
        species_name: str = ""
    ):
        """
        Store alignment result in cache.
        """
        cache_key = self._make_key(primer_seq, template_seq)
        result_json = json.dumps(result)
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO alignment_cache 
            (cache_key, primer_name, species_name, result_json, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (cache_key, primer_name, species_name, result_json, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def delete(self, primer_seq: str, template_seq: str):
        """Delete specific cache entry."""
        cache_key = self._make_key(primer_seq, template_seq)
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alignment_cache WHERE cache_key = ?", (cache_key,))
        conn.commit()
        conn.close()
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        cutoff = datetime.now() - timedelta(days=self.ttl_days)
        
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM alignment_cache 
            WHERE created_at < ?
        """, (cutoff.isoformat(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            logger.info(f"Cleaned up {deleted} expired cache entries")
        
        return deleted
    
    def clear_all(self):
        """Clear entire cache."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM alignment_cache")
        conn.commit()
        conn.close()
        logger.info("Cache cleared")
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        conn = sqlite3.connect(self.cache_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM alignment_cache")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM alignment_cache 
            WHERE created_at > ?
        """, ((datetime.now() - timedelta(days=self.ttl_days)).isoformat(),))
        valid = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total,
            "valid_entries": valid,
            "expired_entries": total - valid,
            "cache_path": self.cache_path
        }


# Global cache instance
_cache_instance = None


def get_cache(cache_path: Optional[str] = None) -> AlignmentCache:
    """Get or create global cache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = AlignmentCache(cache_path)
    return _cache_instance
