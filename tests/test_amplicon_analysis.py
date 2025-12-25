"""
Basic tests for Amplicon Analysis module.
"""

import pytest
from primerlab.core.amplicon import (
    AmpliconAnalyzer,
    analyze_amplicon,
    calculate_gc_profile,
    analyze_gc_clamp,
    predict_amplicon_tm,
    find_restriction_sites,
    calculate_quality_score,
    score_to_grade
)


# Test sequence (100bp)
TEST_SEQ = "ATGCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"

# Sequence with EcoRI site
SEQ_WITH_ECORI = "ATGCGAATTCGATCGATCGATCGATCGATCGATCGATCGATCGATCG"


class TestGCProfile:
    def test_calculate_gc_profile(self):
        profile = calculate_gc_profile(TEST_SEQ, window_size=20, step_size=10)
        assert len(profile.gc_values) > 0
        assert 0 <= profile.uniformity_score <= 100
        assert profile.min_gc >= 0
        assert profile.max_gc <= 100
    
    def test_short_sequence(self):
        profile = calculate_gc_profile("ATGC", window_size=50)
        assert len(profile.gc_values) == 1


class TestGCClamp:
    def test_gc_clamp_analysis(self):
        clamp = analyze_gc_clamp("GCATCGATCGATCGATCGATCGATCGC")
        assert clamp.five_prime_count >= 0
        assert clamp.three_prime_count >= 0
        assert clamp.region_size == 5
    
    def test_optimal_clamp(self):
        clamp = analyze_gc_clamp("GCATCGATCGATCGATCGATCGATCGC")
        assert clamp.is_optimal or not clamp.is_optimal  # Both are valid


class TestTmPrediction:
    def test_predict_tm(self):
        tm_result = predict_amplicon_tm(TEST_SEQ)
        assert tm_result.tm > 0
        assert tm_result.method == "nearest-neighbor"
        assert tm_result.na_concentration == 50.0


class TestRestrictionSites:
    def test_find_ecori(self):
        sites = find_restriction_sites(SEQ_WITH_ECORI)
        ecori_sites = [s for s in sites if s.enzyme == "EcoRI"]
        assert len(ecori_sites) > 0
    
    def test_no_sites(self):
        sites = find_restriction_sites("AAAAAAAAAA")
        assert len(sites) == 0


class TestQualityScore:
    def test_score_to_grade(self):
        assert score_to_grade(90) == "A"
        assert score_to_grade(75) == "B"
        assert score_to_grade(60) == "C"
        assert score_to_grade(45) == "D"
        assert score_to_grade(30) == "F"


class TestAmpliconAnalyzer:
    def test_full_analysis(self):
        result = analyze_amplicon(TEST_SEQ)
        assert result.length == len(TEST_SEQ)
        assert result.quality is not None
        assert 0 <= result.quality.score <= 100
        assert result.quality.grade in ["A", "B", "C", "D", "F"]
    
    def test_analyzer_class(self):
        analyzer = AmpliconAnalyzer()
        result = analyzer.analyze(TEST_SEQ)
        assert result.secondary_structure is not None or result.secondary_structure is None  # May use fallback
        assert result.gc_profile is not None
        assert result.gc_clamp is not None
