"""
Unit tests for probe binding simulation (v0.5.0 Phase 1).
"""

import pytest
from primerlab.core.qpcr.probe_binding import (
    calculate_probe_binding_tm,
    calculate_nearest_neighbor_tm,
    calculate_binding_efficiency,
    simulate_probe_binding,
    ProbeBindingResult,
)
from primerlab.core.qpcr.probe_position import (
    analyze_probe_position,
    optimize_probe_position,
    reverse_complement,
)


class TestProbeBindingTm:
    """Test Tm calculation functions."""
    
    def test_calculate_nearest_neighbor_tm_basic(self):
        """Test basic Tm calculation."""
        probe = "ATGCGATCGATCGATCGATCG"  # 21-mer
        tm, dH, dS = calculate_nearest_neighbor_tm(probe)
        
        assert 50 < tm < 75  # Reasonable range
        assert dH < 0  # Exothermic
        assert dS < 0  # Negative entropy
    
    def test_calculate_probe_binding_tm(self):
        """Test probe Tm calculation."""
        probe = "GCGCGCGCGCGCGCGCGCGC"  # High GC
        tm = calculate_probe_binding_tm(probe)
        
        assert tm > 70  # High GC = high Tm
    
    def test_tm_low_gc(self):
        """Test Tm for low GC probe."""
        probe = "ATATATATATATATATATATAT"  # Low GC
        tm = calculate_probe_binding_tm(probe)
        
        assert tm < 55  # Low GC = low Tm
    
    def test_tm_salt_effect(self):
        """Test salt concentration effect on Tm."""
        probe = "ATGCGATCGATCGATCGATCG"
        
        tm_low = calculate_probe_binding_tm(probe, na_concentration=10.0)
        tm_high = calculate_probe_binding_tm(probe, na_concentration=100.0)
        
        assert tm_high > tm_low  # Higher salt = higher Tm


class TestBindingEfficiency:
    """Test binding efficiency calculation."""
    
    def test_efficiency_optimal(self):
        """Test efficiency at optimal temperature."""
        tm = 70.0
        annealing = 60.0  # 10°C below Tm
        
        efficiency = calculate_binding_efficiency(tm, annealing)
        assert efficiency >= 95
    
    def test_efficiency_too_close(self):
        """Test efficiency when too close to Tm."""
        tm = 70.0
        annealing = 68.0  # Only 2°C below
        
        efficiency = calculate_binding_efficiency(tm, annealing)
        assert efficiency < 90
    
    def test_efficiency_above_tm(self):
        """Test efficiency above Tm."""
        tm = 70.0
        annealing = 72.0  # Above Tm
        
        efficiency = calculate_binding_efficiency(tm, annealing)
        assert efficiency < 50


class TestSimulateProbeBinding:
    """Test full probe binding simulation."""
    
    def test_simulate_basic(self):
        """Test basic simulation."""
        probe = "ATGCGATCGATCGATCGATCG"
        result = simulate_probe_binding(probe)
        
        assert isinstance(result, ProbeBindingResult)
        assert result.probe_tm > 0
        assert result.binding_efficiency >= 0
        assert len(result.binding_curve) > 0
    
    def test_simulate_with_warnings(self):
        """Test simulation generates appropriate warnings."""
        # Short probe
        short_probe = "ATGCGATCG"  # 9 bp
        result = simulate_probe_binding(short_probe)
        
        assert any("short" in w.lower() for w in result.warnings)
    
    def test_simulate_5_g_warning(self):
        """Test 5' G warning."""
        probe = "GCGATCGATCGATCGATCGAT"  # Starts with G
        result = simulate_probe_binding(probe)
        
        assert any("5'" in w or "quench" in w.lower() for w in result.warnings)
    
    def test_grade_assignment(self):
        """Test grade assignment."""
        probe = "ATGCGATCGATCGATCGATCG"  # Good probe
        result = simulate_probe_binding(probe)
        
        assert result.grade in ["A", "B", "C", "D", "F"]
        assert result.score >= 0


class TestProbePosition:
    """Test probe position analysis."""
    
    def test_analyze_position_found(self):
        """Test probe position analysis when probe is in amplicon."""
        amplicon = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        probe = "GATCGATCGATCGATCGATC"
        
        result = analyze_probe_position(probe, amplicon)
        
        assert result.probe_start >= 0
        assert result.position_score > 0
    
    def test_analyze_position_not_found(self):
        """Test probe not found in amplicon."""
        amplicon = "ATGCGATCGATCGATCG"
        probe = "NNNNNNNNNNNNNNNNNNNN"
        
        result = analyze_probe_position(probe, amplicon)
        
        assert result.probe_start == -1
        assert any("not found" in w.lower() for w in result.warnings)
    
    def test_optimize_position(self):
        """Test probe position optimization."""
        amplicon = "A" * 20 + "NNNN" * 30 + "T" * 20  # 140 bp
        
        candidates = optimize_probe_position(
            amplicon,
            fwd_primer_end=10,
            rev_primer_start=130,
            probe_length=20
        )
        
        # May return empty if no good positions (due to N bases)
        assert isinstance(candidates, list)


class TestReverseComplement:
    """Test reverse complement function."""
    
    def test_reverse_complement(self):
        """Test reverse complement calculation."""
        seq = "ATGC"
        rc = reverse_complement(seq)
        
        assert rc == "GCAT"
    
    def test_reverse_complement_long(self):
        """Test longer sequence."""
        seq = "ATGCGATCGATCG"
        rc = reverse_complement(seq)
        
        assert len(rc) == len(seq)
        assert rc == "CGATCGATCGCAT"


class TestProbeBindingAPI:
    """Test API function."""
    
    def test_simulate_probe_binding_api(self):
        """Test public API function."""
        from primerlab.api import simulate_probe_binding_api
        
        probe = "ATGCGATCGATCGATCGATCG"
        result = simulate_probe_binding_api(probe)
        
        assert "probe_tm" in result
        assert "binding_efficiency" in result
        assert "optimal_temp" in result
        assert "binding_curve" in result
        assert "grade" in result
    
    def test_api_with_amplicon(self):
        """Test API with amplicon sequence."""
        from primerlab.api import simulate_probe_binding_api
        
        probe = "GATCGATCGATCGATCGATC"
        amplicon = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"
        
        result = simulate_probe_binding_api(
            probe_sequence=probe,
            amplicon_sequence=amplicon
        )
        
        assert "position" in result
        assert result["position"]["probe_start"] >= 0
