"""Tests for Re-ranking Engine (v0.1.3)."""
import pytest
from unittest.mock import Mock, patch
from primerlab.core.reranking import RerankingEngine


class TestRerankingEngine:
    """Tests for RerankingEngine."""
    
    @pytest.fixture
    def basic_config(self):
        """Basic config for testing."""
        return {
            "parameters": {"show_alternatives": 3},
            "qc": {"mode": "standard"}
        }
    
    @pytest.fixture
    def mock_raw_results(self):
        """Mock Primer3 raw results."""
        return {
            "PRIMER_LEFT_NUM_RETURNED": 3,
            "PRIMER_RIGHT_NUM_RETURNED": 3,
            # Candidate 0
            "PRIMER_LEFT_0_SEQUENCE": "ATGCGATCGATCGATCGC",
            "PRIMER_RIGHT_0_SEQUENCE": "GCTAGCTAGCTAGCTAGC",
            "PRIMER_LEFT_0_TM": 60.0,
            "PRIMER_RIGHT_0_TM": 60.0,
            "PRIMER_LEFT_0_GC_PERCENT": 55.0,
            "PRIMER_RIGHT_0_GC_PERCENT": 55.0,
            "PRIMER_LEFT_0": (10, 18),
            "PRIMER_RIGHT_0": (100, 18),
            "PRIMER_PAIR_0_PRODUCT_SIZE": 90,
            "PRIMER_PAIR_0_PENALTY": 0.5,
            # Candidate 1
            "PRIMER_LEFT_1_SEQUENCE": "TGCATGCATGCATGCATG",
            "PRIMER_RIGHT_1_SEQUENCE": "CATGCATGCATGCATGCA",
            "PRIMER_LEFT_1_TM": 58.0,
            "PRIMER_RIGHT_1_TM": 58.0,
            "PRIMER_LEFT_1_GC_PERCENT": 50.0,
            "PRIMER_RIGHT_1_GC_PERCENT": 50.0,
            "PRIMER_LEFT_1": (15, 18),
            "PRIMER_RIGHT_1": (110, 18),
            "PRIMER_PAIR_1_PRODUCT_SIZE": 95,
            "PRIMER_PAIR_1_PENALTY": 0.8,
            # Candidate 2
            "PRIMER_LEFT_2_SEQUENCE": "AAAAAAAAAAAAAAAAAT",
            "PRIMER_RIGHT_2_SEQUENCE": "TTTTTTTTTTTTTTTTTT",
            "PRIMER_LEFT_2_TM": 45.0,
            "PRIMER_RIGHT_2_TM": 45.0,
            "PRIMER_LEFT_2_GC_PERCENT": 5.0,
            "PRIMER_RIGHT_2_GC_PERCENT": 0.0,
            "PRIMER_LEFT_2": (20, 18),
            "PRIMER_RIGHT_2": (120, 18),
            "PRIMER_PAIR_2_PRODUCT_SIZE": 100,
            "PRIMER_PAIR_2_PENALTY": 5.0,
        }
    
    def test_engine_initialization(self, basic_config):
        """Engine should initialize with proper thresholds."""
        engine = RerankingEngine(basic_config)
        assert engine.hairpin_dg_max == -9.0  # standard mode
        assert engine.homodimer_dg_max == -9.0
        assert engine.heterodimer_dg_max == -9.0
    
    def test_strict_mode(self):
        """Strict mode should have tighter thresholds."""
        config = {"qc": {"mode": "strict"}, "parameters": {}}
        engine = RerankingEngine(config)
        assert engine.hairpin_dg_max == -6.0
    
    def test_relaxed_mode(self):
        """Relaxed mode should have looser thresholds."""
        config = {"qc": {"mode": "relaxed"}, "parameters": {}}
        engine = RerankingEngine(config)
        assert engine.hairpin_dg_max == -12.0
    
    def test_rank_candidates(self, basic_config, mock_raw_results):
        """Ranking should return sorted candidates."""
        engine = RerankingEngine(basic_config)
        
        candidates = engine.rank_candidates(mock_raw_results)
        
        assert len(candidates) == 3
        # Candidates should be sorted (QC-passing first, then by penalty)
        assert all("passes_qc" in c for c in candidates)
        assert all("primer3_penalty" in c for c in candidates)
    
    def test_select_best(self, basic_config, mock_raw_results):
        """select_best should return best and alternatives."""
        engine = RerankingEngine(basic_config)
        
        best, alternatives = engine.select_best(mock_raw_results)
        
        assert best is not None
        assert isinstance(alternatives, list)
        # alternatives should be max 3 (show_alternatives setting)
        assert len(alternatives) <= 3
    
    def test_empty_results(self, basic_config):
        """Empty results should return None and empty list."""
        engine = RerankingEngine(basic_config)
        
        best, alternatives = engine.select_best({"PRIMER_LEFT_NUM_RETURNED": 0})
        
        assert best is None
        assert alternatives == []


class TestQCThresholds:
    """Tests for custom QC thresholds."""
    
    def test_custom_thresholds(self):
        """Custom thresholds should override presets."""
        config = {
            "qc": {
                "mode": "standard",
                "hairpin_dg_max": -5.0,
                "homodimer_dg_max": -7.0
            },
            "parameters": {}
        }
        engine = RerankingEngine(config)
        
        assert engine.hairpin_dg_max == -5.0
        assert engine.homodimer_dg_max == -7.0
        # heterodimer should fallback to preset
        assert engine.heterodimer_dg_max == -9.0
