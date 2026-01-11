"""
Caching utilities for expensive computations.

v0.8.4 - Performance optimization

Provides LRU caching for frequently called functions:
- Tm calculations (primer3)
- GC content calculations
- Delta G calculations (ViennaRNA)

Example:
    >>> from primerlab.core.cache import cached_calc_tm, get_cache_stats
    >>> tm = cached_calc_tm("ATCGATCGATCG")
    >>> print(get_cache_stats())
"""

from functools import lru_cache
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Maximum cache size for each function
TM_CACHE_SIZE = 10000
GC_CACHE_SIZE = 10000


@lru_cache(maxsize=TM_CACHE_SIZE)
def cached_calc_tm(
    sequence: str,
    mv_conc: float = 50.0,
    dv_conc: float = 1.5,
    dntp_conc: float = 0.25,
    dna_conc: float = 50.0
) -> float:
    """
    Calculate Tm with caching.
    
    Uses primer3.calc_tm() with results cached for repeated sequences.
    
    Args:
        sequence: DNA sequence (uppercase)
        mv_conc: Monovalent cation concentration (mM)
        dv_conc: Divalent cation concentration (mM)
        dntp_conc: dNTP concentration (mM)
        dna_conc: DNA concentration (nM)
        
    Returns:
        Melting temperature in Celsius
        
    Example:
        >>> tm = cached_calc_tm("ATCGATCGATCGATCGATCG")
        >>> print(f"Tm: {tm:.1f}°C")
    """
    try:
        import primer3
        return primer3.calc_tm(
            sequence.upper(),
            mv_conc=mv_conc,
            dv_conc=dv_conc,
            dntp_conc=dntp_conc,
            dna_conc=dna_conc
        )
    except ImportError:
        logger.warning("primer3 not installed, returning 0.0 for Tm")
        return 0.0
    except Exception as e:
        logger.debug(f"Tm calculation failed: {e}")
        return 0.0


@lru_cache(maxsize=GC_CACHE_SIZE)
def cached_gc_content(sequence: str) -> float:
    """
    Calculate GC content with caching.
    
    Args:
        sequence: DNA sequence
        
    Returns:
        GC percentage (0-100)
        
    Example:
        >>> gc = cached_gc_content("ATCGATCG")
        >>> print(f"GC: {gc:.1f}%")
    """
    if not sequence:
        return 0.0
    seq_upper = sequence.upper()
    gc_count = sum(1 for c in seq_upper if c in 'GC')
    return (gc_count / len(seq_upper)) * 100


# Delta G cache - uses dict for ViennaRNA results
_dg_cache: Dict[str, Optional[float]] = {}


def cached_delta_g(sequence: str) -> Optional[float]:
    """
    Calculate secondary structure delta G with caching.
    
    Uses ViennaRNA RNAfold for calculation. Results are cached
    to avoid repeated subprocess calls.
    
    Args:
        sequence: DNA/RNA sequence
        
    Returns:
        Delta G in kcal/mol, or None if calculation fails
        
    Example:
        >>> dg = cached_delta_g("ATCGATCGATCG")
        >>> if dg:
        ...     print(f"ΔG: {dg:.1f} kcal/mol")
    """
    if sequence in _dg_cache:
        return _dg_cache[sequence]
    
    try:
        from primerlab.core.tools.vienna_wrapper import ViennaWrapper
        wrapper = ViennaWrapper()
        result = wrapper.fold(sequence)
        dg = result.get('delta_g') if result else None
        _dg_cache[sequence] = dg
        return dg
    except Exception as e:
        logger.debug(f"Delta G calculation failed: {e}")
        _dg_cache[sequence] = None
        return None


def clear_caches() -> None:
    """
    Clear all computation caches.
    
    Useful for testing or when memory needs to be freed.
    
    Example:
        >>> clear_caches()
    """
    cached_calc_tm.cache_clear()
    cached_gc_content.cache_clear()
    _dg_cache.clear()
    logger.debug("All caches cleared")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics for monitoring.
    
    Returns:
        Dictionary with cache info for each cached function
        
    Example:
        >>> stats = get_cache_stats()
        >>> print(f"Tm cache hits: {stats['tm_cache']['hits']}")
    """
    tm_info = cached_calc_tm.cache_info()
    gc_info = cached_gc_content.cache_info()
    
    return {
        "tm_cache": {
            "hits": tm_info.hits,
            "misses": tm_info.misses,
            "size": tm_info.currsize,
            "maxsize": tm_info.maxsize,
            "hit_rate": round(tm_info.hits / max(1, tm_info.hits + tm_info.misses) * 100, 1)
        },
        "gc_cache": {
            "hits": gc_info.hits,
            "misses": gc_info.misses,
            "size": gc_info.currsize,
            "maxsize": gc_info.maxsize,
            "hit_rate": round(gc_info.hits / max(1, gc_info.hits + gc_info.misses) * 100, 1)
        },
        "dg_cache": {
            "size": len(_dg_cache)
        }
    }


# Convenience aliases
calc_tm = cached_calc_tm
gc_content = cached_gc_content
delta_g = cached_delta_g
