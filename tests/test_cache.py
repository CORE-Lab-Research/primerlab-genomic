"""
Tests for cache module (v0.8.4).

Tests LRU caching for Tm, GC, and ΔG calculations.
"""
import pytest
from primerlab.core.cache import (
    cached_calc_tm,
    cached_gc_content,
    cached_delta_g,
    clear_caches,
    get_cache_stats
)


class TestCachedGCContent:
    """Tests for GC content caching."""
    
    def test_gc_content_basic(self):
        """Test basic GC calculation."""
        # Clear cache first
        clear_caches()
        
        gc = cached_gc_content("ATCGATCG")
        assert gc == 50.0  # 4 G/C out of 8
        
    def test_gc_content_all_gc(self):
        """Test sequence with all G/C."""
        gc = cached_gc_content("GCGCGCGC")
        assert gc == 100.0
        
    def test_gc_content_no_gc(self):
        """Test sequence with no G/C."""
        gc = cached_gc_content("ATATAT")
        assert gc == 0.0
        
    def test_gc_content_empty(self):
        """Test empty sequence."""
        gc = cached_gc_content("")
        assert gc == 0.0
        
    def test_gc_content_caching(self):
        """Test that caching works."""
        clear_caches()
        
        # First call - miss
        cached_gc_content("ATCGATCGATCG")
        stats1 = get_cache_stats()
        
        # Second call - should be hit
        cached_gc_content("ATCGATCGATCG")
        stats2 = get_cache_stats()
        
        assert stats2["gc_cache"]["hits"] > stats1["gc_cache"]["hits"]
        
    def test_gc_content_lowercase(self):
        """Test lowercase sequence handling."""
        gc_lower = cached_gc_content("atcgatcg")
        gc_upper = cached_gc_content("ATCGATCG")
        # Note: lowercase and uppercase are cached separately
        assert gc_lower == 50.0
        assert gc_upper == 50.0


class TestCachedTm:
    """Tests for Tm caching."""
    
    def test_tm_returns_float(self):
        """Test Tm returns a float."""
        clear_caches()
        tm = cached_calc_tm("ATCGATCGATCGATCGATCG")
        assert isinstance(tm, float)
        
    def test_tm_caching(self):
        """Test that Tm caching works."""
        clear_caches()
        
        seq = "GCGCATCGATCGATCGATCG"
        
        # First call
        cached_calc_tm(seq)
        stats1 = get_cache_stats()
        
        # Second call - same sequence
        cached_calc_tm(seq)
        stats2 = get_cache_stats()
        
        assert stats2["tm_cache"]["hits"] > stats1["tm_cache"]["hits"]
        
    def test_tm_different_params(self):
        """Test Tm with different parameters."""
        clear_caches()
        
        seq = "ATCGATCGATCGATCGATCG"
        
        tm1 = cached_calc_tm(seq, mv_conc=50.0)
        tm2 = cached_calc_tm(seq, mv_conc=100.0)
        
        # Different params should give different results (if primer3 is installed)
        # Both should be valid floats
        assert isinstance(tm1, float)
        assert isinstance(tm2, float)


class TestCachedDeltaG:
    """Tests for Delta G caching."""
    
    def test_delta_g_caching(self):
        """Test that delta G results are cached."""
        clear_caches()
        
        seq = "GCGCGCGCGC"
        
        # First call
        dg1 = cached_delta_g(seq)
        stats1 = get_cache_stats()
        
        # Second call - should use cache
        dg2 = cached_delta_g(seq)
        stats2 = get_cache_stats()
        
        # Results should be same
        assert dg1 == dg2
        
        # Cache size should not increase on second call
        # (might be None if ViennaRNA not installed)
        

class TestCacheStats:
    """Tests for cache statistics."""
    
    def test_get_cache_stats(self):
        """Test cache stats structure."""
        stats = get_cache_stats()
        
        assert "tm_cache" in stats
        assert "gc_cache" in stats
        assert "dg_cache" in stats
        
        assert "hits" in stats["tm_cache"]
        assert "misses" in stats["tm_cache"]
        assert "size" in stats["tm_cache"]
        assert "hit_rate" in stats["tm_cache"]
        
    def test_clear_caches(self):
        """Test cache clearing."""
        # Add some items
        cached_gc_content("ATCG")
        cached_gc_content("GCGC")
        
        stats_before = get_cache_stats()
        assert stats_before["gc_cache"]["size"] >= 2
        
        # Clear
        clear_caches()
        
        stats_after = get_cache_stats()
        assert stats_after["gc_cache"]["size"] == 0
        assert stats_after["tm_cache"]["size"] == 0
        assert stats_after["dg_cache"]["size"] == 0


class TestCacheHitRate:
    """Tests for cache hit rate calculation."""
    
    def test_hit_rate_calculation(self):
        """Test hit rate is calculated correctly."""
        clear_caches()
        
        # 1 miss
        cached_gc_content("AAAA")
        
        # 1 hit
        cached_gc_content("AAAA")
        
        stats = get_cache_stats()
        
        # Hit rate should be 50% (1 hit, 1 miss)
        assert stats["gc_cache"]["hit_rate"] == 50.0
