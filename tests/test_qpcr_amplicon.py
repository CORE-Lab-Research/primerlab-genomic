"""
Unit tests for qPCR amplicon validation (v0.5.0 Phase 2).
"""

import pytest
from primerlab.core.qpcr.amplicon_qc import (
    calculate_gc_content,
    estimate_amplicon_tm,
    estimate_secondary_structure_dg,
    validate_qpcr_amplicon,
    score_qpcr_efficiency,
    QpcrAmpliconQC,
    QPCR_AMPLICON_MIN,
    QPCR_AMPLICON_MAX,
)


class TestGCContent:
    """Test GC content calculation."""
    
    def test_gc_50_percent(self):
        """Test 50% GC sequence."""
        seq = "ATGC" * 10  # 50% GC
        gc = calculate_gc_content(seq)
        assert gc == 50.0
    
    def test_gc_all_gc(self):
        """Test 100% GC sequence."""
        seq = "GCGCGCGCGC"
        gc = calculate_gc_content(seq)
        assert gc == 100.0
    
    def test_gc_no_gc(self):
        """Test 0% GC sequence."""
        seq = "ATATATATAT"
        gc = calculate_gc_content(seq)
        assert gc == 0.0
    
    def test_gc_empty(self):
        """Test empty sequence."""
        gc = calculate_gc_content("")
        assert gc == 0.0


class TestAmpliconTm:
    """Test amplicon Tm estimation."""
    
    def test_tm_calculation(self):
        """Test basic Tm calculation."""
        seq = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        tm = estimate_amplicon_tm(seq)
        
        assert 70 < tm < 95  # Reasonable range for 100bp
    
    def test_tm_short(self):
        """Test Tm for short sequence."""
        seq = "ATGCGATCGATCGATCGATCG"
        tm = estimate_amplicon_tm(seq)
        
        assert tm > 0
    
    def test_tm_empty(self):
        """Test empty sequence."""
        tm = estimate_amplicon_tm("")
        assert tm == 0.0


class TestSecondaryStructure:
    """Test secondary structure estimation."""
    
    def test_dg_gc_rich(self):
        """Test ΔG for GC-rich sequence."""
        seq = "GCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGC"
        dg = estimate_secondary_structure_dg(seq)
        
        # Should be negative (stable)
        assert dg < 0
    
    def test_dg_at_rich(self):
        """Test ΔG for AT-rich sequence."""
        seq = "ATATATATATATATATATATATATATATATAT"
        dg = estimate_secondary_structure_dg(seq)
        
        # Should be less negative
        assert dg > -3.0
    
    def test_dg_short(self):
        """Test short sequence."""
        dg = estimate_secondary_structure_dg("ATGC")
        assert dg == 0.0


class TestValidateQpcrAmplicon:
    """Test qPCR amplicon validation."""
    
    def test_optimal_amplicon(self):
        """Test optimal amplicon."""
        # Create 100bp sequence with ~50% GC
        seq = "ATGC" * 25  # 100bp, 50% GC
        
        result = validate_qpcr_amplicon(seq)
        
        assert isinstance(result, QpcrAmpliconQC)
        assert result.length_ok
        assert result.gc_ok
        assert result.grade in ["A", "B"]
    
    def test_too_short(self):
        """Test amplicon too short."""
        seq = "ATGC" * 10  # 40bp
        
        result = validate_qpcr_amplicon(seq)
        
        assert not result.length_ok
        assert any("short" in w.lower() for w in result.warnings)
    
    def test_too_long(self):
        """Test amplicon too long."""
        seq = "ATGC" * 100  # 400bp
        
        result = validate_qpcr_amplicon(seq)
        
        assert not result.length_ok
        assert any("long" in w.lower() for w in result.warnings)
    
    def test_gc_too_low(self):
        """Test low GC content."""
        seq = "ATAT" * 25  # 0% GC
        
        result = validate_qpcr_amplicon(seq)
        
        assert not result.gc_ok
        assert any("gc" in w.lower() and "low" in w.lower() for w in result.warnings)
    
    def test_gc_too_high(self):
        """Test high GC content."""
        seq = "GCGC" * 25  # 100% GC
        
        result = validate_qpcr_amplicon(seq)
        
        assert not result.gc_ok
        assert any("gc" in w.lower() and "high" in w.lower() for w in result.warnings)
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        seq = "ATGC" * 25
        result = validate_qpcr_amplicon(seq)
        
        d = result.to_dict()
        
        assert "amplicon_length" in d
        assert "gc_content" in d
        assert "quality_score" in d
        assert "grade" in d


class TestEfficiencyScoring:
    """Test qPCR efficiency scoring."""
    
    def test_optimal_efficiency(self):
        """Test optimal conditions."""
        eff = score_qpcr_efficiency(
            amplicon_length=100,
            primer_tm_diff=0.5,
        )
        
        assert eff >= 95
    
    def test_long_amplicon_penalty(self):
        """Test longer amplicon reduces efficiency."""
        eff_short = score_qpcr_efficiency(amplicon_length=100, primer_tm_diff=0.5)
        eff_long = score_qpcr_efficiency(amplicon_length=200, primer_tm_diff=0.5)
        
        assert eff_short > eff_long
    
    def test_tm_difference_penalty(self):
        """Test Tm difference penalty."""
        eff_balanced = score_qpcr_efficiency(amplicon_length=100, primer_tm_diff=0.5)
        eff_unbalanced = score_qpcr_efficiency(amplicon_length=100, primer_tm_diff=5.0)
        
        assert eff_balanced > eff_unbalanced
    
    def test_probe_tm_effect(self):
        """Test probe Tm effect."""
        eff_optimal = score_qpcr_efficiency(
            amplicon_length=100, primer_tm_diff=0.5, probe_tm_diff=8.0
        )
        eff_suboptimal = score_qpcr_efficiency(
            amplicon_length=100, primer_tm_diff=0.5, probe_tm_diff=15.0
        )
        
        assert eff_optimal > eff_suboptimal
    
    def test_efficiency_range(self):
        """Test efficiency stays in valid range."""
        # Very bad conditions
        eff = score_qpcr_efficiency(
            amplicon_length=300,
            primer_tm_diff=10.0,
            hairpin_penalty=20.0,
            dimer_penalty=20.0,
        )
        
        assert 70 <= eff <= 110
