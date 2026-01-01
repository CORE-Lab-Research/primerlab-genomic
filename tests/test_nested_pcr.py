"""
Unit tests for Nested PCR module.
"""

import pytest
from primerlab.core.variants.models import NestedPrimerSet, NestedPCRResult
from primerlab.core.variants.nested import NestedPCREngine, design_nested_primers


# Test sequence (~800bp for nested PCR)
TEST_SEQUENCE = (
    "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACAAATTTTCTGTC"
    "AGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGGAAAACTACCTGTTCCATGGCCA"
    "ACACTTGTCACTACTTTCTCTTATGGTGTTCAATGCTTTTCAAGATACCCAGATCATATGAAACGGCATGACTTTTTCAAGAGTGCC"
    "ATGCCCGAAGGTTATGTACAGGAAAGAACTATATTTTTCAAAGATGACGGGAACTACAAGACACGTGCTGAAGTCAAGTTTGAAGGT"
    "GATACCCTTGTTAATAGAATCGAGTTAAAAGGTATTGATTTTAAAGAAGATGGAAACATTCTTGGACACAAATTGGAATACAACTAT"
    "AACTCACACAATGTATACATCATGGCAGACAAACAAAAGAATGGAATCAAAGTTAACTTCAAAATTAGACACAACATTGAAGATGGA"
    "AGCGTTCAACTAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTACCAGACAACCATTACCTGTCCACA"
    "CAATCTGCCCTTTCGAAAGATCCCAACGAAAAGAGAGACCACATGGTCCTTCTTGAGTTTGTAACAGCTGCTGGGATTACACATGGC"
    "ATGGATGAACTATACAAATAA"
)


class TestNestedPrimerSet:
    """Tests for NestedPrimerSet model."""
    
    def test_creation(self):
        """Test NestedPrimerSet creation."""
        ns = NestedPrimerSet(
            outer_forward="ATGAGTAAAGGAGAAGAACT",
            outer_reverse="TTATTTGTAGTCATCCATGC",
            outer_tm_forward=58.0,
            outer_tm_reverse=57.5,
            outer_gc_forward=40.0,
            outer_gc_reverse=42.0,
            outer_start=0,
            outer_end=500,
            outer_product_size=500,
            inner_forward="ACTGGAGTTGTCCCAATTCT",
            inner_reverse="CCATGGCCAACACTTGTCAC",
            inner_tm_forward=60.0,
            inner_tm_reverse=61.0,
            inner_gc_forward=50.0,
            inner_gc_reverse=55.0,
            inner_start=20,
            inner_end=200,
            inner_product_size=180,
        )
        
        assert ns.outer_forward == "ATGAGTAAAGGAGAAGAACT"
        assert ns.inner_forward == "ACTGGAGTTGTCCCAATTCT"
        assert ns.outer_product_size == 500
        assert ns.inner_product_size == 180
    
    def test_tm_difference(self):
        """Test Tm difference calculation."""
        ns = NestedPrimerSet(
            outer_forward="ATGAGTAAAGGAGAAGAACT",
            outer_reverse="TTATTTGTAGTCATCCATGC",
            outer_tm_forward=58.0,
            outer_tm_reverse=58.0,
            outer_gc_forward=40.0,
            outer_gc_reverse=42.0,
            outer_start=0,
            outer_end=500,
            outer_product_size=500,
            inner_forward="ACTGGAGTTGTCCCAATTCT",
            inner_reverse="CCATGGCCAACACTTGTCAC",
            inner_tm_forward=60.0,
            inner_tm_reverse=60.0,
            inner_gc_forward=50.0,
            inner_gc_reverse=55.0,
            inner_start=20,
            inner_end=200,
            inner_product_size=180,
        )
        
        # Inner avg (60) - Outer avg (58) = 2
        assert ns.get_tm_difference() == 2.0
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        ns = NestedPrimerSet(
            outer_forward="ATGAGTAAAGGAGAAGAACT",
            outer_reverse="TTATTTGTAGTCATCCATGC",
            outer_tm_forward=58.0,
            outer_tm_reverse=58.0,
            outer_gc_forward=40.0,
            outer_gc_reverse=42.0,
            outer_start=0,
            outer_end=500,
            outer_product_size=500,
            inner_forward="ACTGGAGTTGTCCCAATTCT",
            inner_reverse="CCATGGCCAACACTTGTCAC",
            inner_tm_forward=60.0,
            inner_tm_reverse=60.0,
            inner_gc_forward=50.0,
            inner_gc_reverse=55.0,
            inner_start=20,
            inner_end=200,
            inner_product_size=180,
        )
        
        d = ns.to_dict()
        assert "outer" in d
        assert "inner" in d
        assert d["outer"]["forward"] == "ATGAGTAAAGGAGAAGAACT"
        assert d["inner"]["forward"] == "ACTGGAGTTGTCCCAATTCT"


class TestNestedPCRResult:
    """Tests for NestedPCRResult model."""
    
    def test_creation_empty(self):
        """Test empty result creation."""
        result = NestedPCRResult()
        assert result.success is False
        assert result.primer_set is None
        assert result.alternatives == []
    
    def test_to_dict(self):
        """Test dictionary conversion."""
        result = NestedPCRResult(
            success=False,
            warnings=["Test warning"],
            outer_size_range=(400, 600),
            inner_size_range=(100, 200),
        )
        
        d = result.to_dict()
        assert d["success"] is False
        assert d["warnings"] == ["Test warning"]
        assert d["parameters"]["outer_size_range"] == (400, 600)


class TestNestedPCREngine:
    """Tests for NestedPCREngine."""
    
    def test_engine_creation(self):
        """Test engine creation with default config."""
        engine = NestedPCREngine()
        assert engine.outer_size_min == 400
        assert engine.outer_size_max == 600
        assert engine.inner_size_min == 100
        assert engine.inner_size_max == 200
    
    def test_engine_custom_config(self):
        """Test engine with custom config."""
        config = {
            "outer_size_min": 300,
            "outer_size_max": 500,
            "inner_size_min": 80,
            "inner_size_max": 150,
        }
        engine = NestedPCREngine(config)
        assert engine.outer_size_min == 300
        assert engine.inner_size_max == 150
    
    def test_design_short_sequence(self):
        """Test design with too short sequence."""
        engine = NestedPCREngine()
        result = engine.design("ATGC" * 50)  # 200bp
        
        assert result.success is False
        assert len(result.warnings) > 0
        assert "too short" in result.warnings[0].lower()
    
    def test_design_valid_sequence(self):
        """Test design with valid sequence."""
        engine = NestedPCREngine({
            "outer_size_min": 200,
            "outer_size_max": 400,
            "inner_size_min": 80,
            "inner_size_max": 150,
        })
        result = engine.design(TEST_SEQUENCE)
        
        # Should succeed or at least not crash
        assert isinstance(result, NestedPCRResult)
        assert result.sequence_length == len(TEST_SEQUENCE)


class TestDesignNestedPrimers:
    """Tests for design_nested_primers function."""
    
    def test_function_call(self):
        """Test function call with defaults."""
        result = design_nested_primers(
            sequence=TEST_SEQUENCE,
            outer_size_range=(200, 400),
            inner_size_range=(80, 150),
        )
        
        assert isinstance(result, NestedPCRResult)
        assert result.outer_size_range == (200, 400)
        assert result.inner_size_range == (80, 150)
    
    def test_function_custom_tm(self):
        """Test function with custom Tm."""
        result = design_nested_primers(
            sequence=TEST_SEQUENCE,
            outer_size_range=(200, 400),
            inner_size_range=(80, 150),
            outer_tm=56.0,
            inner_tm=58.0,
        )
        
        assert isinstance(result, NestedPCRResult)
