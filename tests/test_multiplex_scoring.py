"""
Unit tests for Multiplex Scoring Engine.

Tests:
- MULTIPLEX_CONFIG preset modes
- MultiplexScorer initialization
- Component score calculations
- User config overrides
- Edge cases (empty matrix, single pair)
"""

import pytest
from primerlab.core.multiplex.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
)
from primerlab.core.multiplex.scoring import (
    MultiplexScorer,
    MULTIPLEX_CONFIG,
)


class TestMultiplexConfig:
    """Tests for MULTIPLEX_CONFIG presets."""
    
    def test_all_modes_exist(self):
        """Test all expected modes are defined."""
        assert "strict" in MULTIPLEX_CONFIG
        assert "standard" in MULTIPLEX_CONFIG
        assert "relaxed" in MULTIPLEX_CONFIG
    
    def test_strict_has_tighter_thresholds(self):
        """Test strict mode has tighter thresholds than standard."""
        strict = MULTIPLEX_CONFIG["strict"]
        standard = MULTIPLEX_CONFIG["standard"]
        
        # Strict should have higher (less negative) threshold
        assert strict["dimer_dg_threshold"] > standard["dimer_dg_threshold"]
        # Strict should have smaller Tm diff allowed
        assert strict["tm_diff_max"] < standard["tm_diff_max"]
    
    def test_relaxed_has_looser_thresholds(self):
        """Test relaxed mode has looser thresholds than standard."""
        relaxed = MULTIPLEX_CONFIG["relaxed"]
        standard = MULTIPLEX_CONFIG["standard"]
        
        # Relaxed should have lower (more negative) threshold
        assert relaxed["dimer_dg_threshold"] < standard["dimer_dg_threshold"]
        # Relaxed should have larger Tm diff allowed
        assert relaxed["tm_diff_max"] > standard["tm_diff_max"]
    
    def test_weights_sum_to_one(self):
        """Test that weights sum to approximately 1.0."""
        for mode, config in MULTIPLEX_CONFIG.items():
            total = (
                config["dimer_weight"] +
                config["tm_weight"] +
                config["gc_weight"] +
                config["count_weight"]
            )
            assert abs(total - 1.0) < 0.01, f"{mode} weights don't sum to 1.0"


class TestMultiplexScorerInit:
    """Tests for MultiplexScorer initialization."""
    
    def test_default_initialization(self):
        """Test default initialization uses standard mode."""
        scorer = MultiplexScorer()
        assert scorer.mode == "standard"
    
    def test_custom_mode(self):
        """Test custom mode selection."""
        config = {"multiplex": {"mode": "strict"}}
        scorer = MultiplexScorer(config)
        assert scorer.mode == "strict"
    
    def test_invalid_mode_fallback(self):
        """Test invalid mode falls back to standard."""
        config = {"multiplex": {"mode": "invalid_mode"}}
        scorer = MultiplexScorer(config)
        assert scorer.mode == "standard"
    
    def test_user_override(self):
        """Test user can override individual settings."""
        config = {
            "multiplex": {
                "mode": "standard",
                "dimer_dg_threshold": -7.0,  # Override
            }
        }
        scorer = MultiplexScorer(config)
        assert scorer.settings["dimer_dg_threshold"] == -7.0
    
    def test_nested_scoring_override(self):
        """Test nested scoring section overrides weights."""
        config = {
            "multiplex": {
                "scoring": {
                    "dimer_weight": 0.50,
                }
            }
        }
        scorer = MultiplexScorer(config)
        assert scorer.settings["dimer_weight"] == 0.50


class TestDimerScoring:
    """Tests for dimer score calculation."""
    
    def test_empty_matrix_full_score(self):
        """Test empty matrix returns full score."""
        scorer = MultiplexScorer()
        matrix = CompatibilityMatrix()
        
        score, warnings = scorer.calculate_dimer_score(matrix)
        assert score == 100.0
        assert len(warnings) == 0
    
    def test_no_problematic_dimers(self):
        """Test no problematic dimers returns full score."""
        scorer = MultiplexScorer()
        
        good_dimer = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-3.0,
            is_problematic=False,
        )
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            matrix={("P1", "P2"): good_dimer},
            total_dimers=1,
            problematic_count=0,
        )
        
        score, warnings = scorer.calculate_dimer_score(matrix)
        assert score == 100.0
    
    def test_problematic_dimer_reduces_score(self):
        """Test problematic dimers reduce score."""
        scorer = MultiplexScorer()
        
        bad_dimer = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-10.0,  # Very stable (bad)
            is_problematic=True,
        )
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            matrix={("P1", "P2"): bad_dimer},
            total_dimers=1,
            problematic_count=1,
            worst_dimer=bad_dimer,
        )
        
        score, warnings = scorer.calculate_dimer_score(matrix)
        assert score < 100.0
        assert len(warnings) > 0  # Should have warning for severe dimer


class TestTmScoring:
    """Tests for Tm score calculation."""
    
    def test_single_pair_full_score(self):
        """Test single pair returns full score."""
        scorer = MultiplexScorer()
        pairs = [MultiplexPair("P1", "ATGC", "GCTA", tm_forward=60.0, tm_reverse=60.0)]
        
        score, warnings = scorer.calculate_tm_score(pairs)
        assert score == 100.0
    
    def test_uniform_tm_high_score(self):
        """Test uniform Tm values give high score."""
        scorer = MultiplexScorer()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", tm_forward=60.0, tm_reverse=60.0),
            MultiplexPair("P2", "TTTT", "AAAA", tm_forward=60.0, tm_reverse=60.0),
        ]
        
        score, warnings = scorer.calculate_tm_score(pairs)
        assert score >= 95.0  # Very uniform
    
    def test_spread_tm_lower_score(self):
        """Test spread Tm values give lower score."""
        scorer = MultiplexScorer()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", tm_forward=55.0, tm_reverse=55.0),
            MultiplexPair("P2", "TTTT", "AAAA", tm_forward=65.0, tm_reverse=65.0),
        ]
        
        score, warnings = scorer.calculate_tm_score(pairs)
        assert score < 90.0  # 10°C spread should reduce score


class TestGcScoring:
    """Tests for GC score calculation."""
    
    def test_uniform_gc_high_score(self):
        """Test uniform GC values give high score."""
        scorer = MultiplexScorer()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", gc_forward=50.0, gc_reverse=50.0),
            MultiplexPair("P2", "TTTT", "AAAA", gc_forward=50.0, gc_reverse=50.0),
        ]
        
        score, warnings = scorer.calculate_gc_score(pairs)
        assert score >= 95.0


class TestCountScoring:
    """Tests for count score calculation."""
    
    def test_small_set_full_score(self):
        """Test 2 pairs or less returns full score."""
        scorer = MultiplexScorer()
        
        score, warnings = scorer.calculate_count_score(2)
        assert score == 100.0
    
    def test_larger_set_reduced_score(self):
        """Test larger sets have reduced score."""
        scorer = MultiplexScorer()
        
        score_5, _ = scorer.calculate_count_score(5)
        score_10, warnings = scorer.calculate_count_score(10)
        
        assert score_5 < 100.0
        assert score_10 < score_5


class TestOverallScore:
    """Tests for overall score calculation."""
    
    def test_calculate_score_returns_result(self):
        """Test calculate_score returns MultiplexResult."""
        scorer = MultiplexScorer()
        
        pairs = [MultiplexPair("P1", "ATGC", "GCTA")]
        matrix = CompatibilityMatrix()
        
        result = scorer.calculate_score(matrix, pairs)
        
        assert result.score >= 0.0
        assert result.score <= 100.0
        assert result.grade in ("A", "B", "C", "D", "F")
    
    def test_config_used_tracked(self):
        """Test config used is tracked in result."""
        config = {"multiplex": {"mode": "strict"}}
        scorer = MultiplexScorer(config)
        
        pairs = [MultiplexPair("P1", "ATGC", "GCTA")]
        matrix = CompatibilityMatrix()
        
        result = scorer.calculate_score(matrix, pairs)
        
        assert result.config_used["mode"] == "strict"
        assert "component_scores" in result.config_used
