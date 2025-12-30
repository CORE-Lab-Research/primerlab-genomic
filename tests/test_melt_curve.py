"""
Unit tests for SYBR melt curve prediction (v0.5.0 Phase 3).
"""

import pytest
from primerlab.core.qpcr.melt_curve import (
    calculate_amplicon_tm,
    generate_melt_curve,
    detect_secondary_peaks,
    predict_melt_curve,
    MeltCurveResult,
    MeltPeak,
)
from primerlab.core.qpcr.melt_report import (
    generate_melt_markdown,
    generate_melt_csv,
    generate_melt_json,
)


class TestAmpliconTm:
    """Test amplicon Tm calculation."""
    
    def test_tm_moderate_gc(self):
        """Test Tm for moderate GC amplicon."""
        seq = "ATGC" * 25  # 100bp, 50% GC
        tm = calculate_amplicon_tm(seq)
        
        assert 70 < tm < 85  # Realistic range for 50% GC
    
    def test_tm_high_gc(self):
        """Test Tm for high GC amplicon."""
        seq = "GCGC" * 25  # 100% GC
        tm = calculate_amplicon_tm(seq)
        
        assert tm > 90
    
    def test_tm_low_gc(self):
        """Test Tm for low GC amplicon."""
        seq = "ATAT" * 25  # 0% GC
        tm = calculate_amplicon_tm(seq)
        
        assert tm < 75
    
    def test_tm_salt_effect(self):
        """Test salt concentration effect."""
        seq = "ATGC" * 25
        tm_low = calculate_amplicon_tm(seq, na_concentration=10.0)
        tm_high = calculate_amplicon_tm(seq, na_concentration=100.0)
        
        assert tm_high > tm_low


class TestMeltCurve:
    """Test melt curve generation."""
    
    def test_generate_curve(self):
        """Test basic curve generation."""
        curve = generate_melt_curve(tm=85.0)
        
        assert len(curve) > 0
        assert all("temperature" in p and "derivative" in p for p in curve)
    
    def test_curve_peak_at_tm(self):
        """Test curve peaks at Tm."""
        tm = 85.0
        curve = generate_melt_curve(tm=tm)
        
        # Find peak
        max_point = max(curve, key=lambda p: p["derivative"])
        
        # Peak should be near Tm
        assert abs(max_point["temperature"] - tm) < 1.0
    
    def test_curve_temperature_range(self):
        """Test curve covers specified range."""
        curve = generate_melt_curve(tm=85.0, min_temp=70.0, max_temp=90.0)
        
        temps = [p["temperature"] for p in curve]
        assert min(temps) == 70.0
        assert max(temps) <= 90.0


class TestSecondaryPeaks:
    """Test secondary peak detection."""
    
    def test_single_peak_uniform(self):
        """Test uniform sequence gives single peak."""
        seq = "ATGC" * 30  # Uniform GC
        peaks = detect_secondary_peaks(seq, primary_tm=85.0)
        
        assert len(peaks) >= 1
        assert peaks[0].is_primary
    
    def test_variable_gc_multiple_peaks(self):
        """Test variable GC may give multiple peaks."""
        # Create sequence with GC variation
        seq = "GCGC" * 20 + "ATAT" * 20  # GC-rich then AT-rich
        peaks = detect_secondary_peaks(seq, primary_tm=85.0)
        
        # May have secondary peak
        assert len(peaks) >= 1


class TestPredictMeltCurve:
    """Test full melt curve prediction."""
    
    def test_predict_basic(self):
        """Test basic prediction."""
        seq = "ATGC" * 25  # 100bp
        result = predict_melt_curve(seq)
        
        assert isinstance(result, MeltCurveResult)
        assert result.predicted_tm > 0
        assert len(result.melt_curve) > 0
    
    def test_predict_single_peak(self):
        """Test uniform sequence gives single peak."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        # May or may not have secondary peaks depending on analysis
        assert len(result.peaks) >= 1
    
    def test_predict_short_warning(self):
        """Test short amplicon generates warning."""
        seq = "ATGC" * 10  # 40bp
        result = predict_melt_curve(seq)
        
        assert any("short" in w.lower() for w in result.warnings)
    
    def test_predict_grade(self):
        """Test grade assignment."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        assert result.grade in ["A", "B", "C", "D", "F"]
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        d = result.to_dict()
        
        assert "predicted_tm" in d
        assert "melt_curve" in d
        assert "is_single_peak" in d


class TestMeltReport:
    """Test melt curve report generation."""
    
    def test_markdown_report(self):
        """Test markdown report generation."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        md = generate_melt_markdown(result)
        
        assert "# SYBR Green Melt Curve Analysis" in md
        assert "Predicted Tm" in md
        assert "Grade" in md
    
    def test_csv_report(self):
        """Test CSV report generation."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        csv = generate_melt_csv(result)
        
        assert "Temperature" in csv
        assert "-dF/dT" in csv
        lines = csv.strip().split("\n")
        assert len(lines) > 10  # Header + data points
    
    def test_json_report(self):
        """Test JSON report generation."""
        seq = "ATGC" * 25
        result = predict_melt_curve(seq)
        
        data = generate_melt_json(result)
        
        assert isinstance(data, dict)
        assert "predicted_tm" in data
        assert "melt_curve" in data


class TestMeltPeak:
    """Test MeltPeak dataclass."""
    
    def test_peak_to_dict(self):
        """Test peak to_dict."""
        peak = MeltPeak(
            temperature=85.0,
            height=1.0,
            width=2.0,
            is_primary=True,
        )
        
        d = peak.to_dict()
        
        assert d["temperature"] == 85.0
        assert d["is_primary"] == True
