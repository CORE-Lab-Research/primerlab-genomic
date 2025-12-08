"""Tests for sequence QC utilities (GC Clamp, Poly-X)."""
import pytest
from primerlab.core.sequence_qc import (
    check_gc_clamp,
    check_poly_x,
    check_3prime_stability,
    run_sequence_qc
)


class TestGCClamp:
    """Tests for GC Clamp check."""
    
    def test_good_gc_clamp(self):
        """Primer with 2 G/C in last 5 bases should pass."""
        seq = "ATATATGCATGC"  # Last 5: ATGC (3 G/C - C at end)
        passed, msg, explanation = check_gc_clamp(seq)
        assert passed
        assert "Good" in msg
    
    def test_weak_gc_clamp(self):
        """Primer with 0 G/C in last 5 bases should fail."""
        seq = "ATATATAT"  # Last 5: TATAT (0 G/C)
        passed, msg, explanation = check_gc_clamp(seq)
        assert not passed
        assert "Weak" in msg
        assert "poor annealing" in explanation
    
    def test_strong_gc_clamp(self):
        """Primer with 5 G/C in last 5 bases should PASS with warning (not fail)."""
        seq = "ATGCGCGCG"  # Last 5: GCGCG (5 G/C)
        passed, msg, explanation = check_gc_clamp(seq)
        # Strong GC is now a WARNING, not failure
        assert passed  # Changed: Strong now passes
        assert "Strong" in msg
        assert "non-specific binding" in explanation
    
    def test_short_sequence(self):
        """Short sequences should still be checked."""
        seq = "GC"
        passed, msg, explanation = check_gc_clamp(seq)
        assert passed  # 2 G/C in 2 bases is fine


class TestPolyX:
    """Tests for Poly-X run detection."""
    
    def test_no_poly_run(self):
        """Sequence with no runs should pass."""
        seq = "ATGCATGCATGC"
        passed, msg = check_poly_x(seq)
        assert passed
    
    def test_poly_a_detected(self):
        """Sequence with AAAAA (5 consecutive) should fail."""
        seq = "ATGCAAAAATGC"
        passed, msg = check_poly_x(seq, max_run=4)
        assert not passed
        assert "Poly-A" in msg
    
    def test_poly_g_detected(self):
        """Sequence with GGGGG should fail."""
        seq = "ATGGGGGCAT"
        passed, msg = check_poly_x(seq, max_run=4)
        assert not passed
        assert "Poly-G" in msg
    
    def test_max_4_allowed(self):
        """Sequence with 4 consecutive (exactly max) should pass."""
        seq = "ATGAAAATGC"  # 4 A's
        passed, msg = check_poly_x(seq, max_run=4)
        assert passed


class TestIntegration:
    """Integration tests for run_sequence_qc."""
    
    def test_good_primer(self):
        """Good primer with optimal GC clamp should pass all checks."""
        seq = "ATGCGATCGATCGATATC"  # Last 5: ATATC (1 G/C) - optimal range
        result = run_sequence_qc(seq)
        assert result["passes_all"]
    
    def test_strong_gc_primer(self):
        """Primer with strong GC clamp should pass but have warning."""
        seq = "ATGCGATCGATCGATCGC"  # Last 5: TCGCC (4 G/C) - strong but OK
        result = run_sequence_qc(seq)
        assert result["passes_all"]  # Still passes
        # May have warning for strong GC
    
    def test_bad_primer(self):
        """Bad primer should fail with warnings."""
        seq = "ATAAATAAAAAAT"  # Weak GC clamp + poly-A (5+ consecutive)
        result = run_sequence_qc(seq)
        assert not result["passes_all"]
        assert len(result["warnings"]) > 0
