"""
Unit tests for genotyping module (v0.6.0 Phase 1).
"""

import pytest
from primerlab.core.genotyping.allele_scoring import (
    score_allele_discrimination,
    AlleleScoringResult,
)
from primerlab.core.genotyping.snp_position import (
    validate_snp_position,
    analyze_snp_context,
)
from primerlab.core.genotyping.discrimination_tm import (
    calculate_discrimination_tm,
    estimate_allele_specificity,
)


class TestAlleleScoringResult:
    """Test AlleleScoringResult dataclass."""
    
    def test_to_dict(self):
        """Test to_dict conversion."""
        result = AlleleScoringResult(
            primer_sequence="ATGCGATCGATCGATCG",
            snp_position=0,
            ref_allele="A",
            alt_allele="T",
            position_score=100.0,
            mismatch_score=100.0,
            combined_score=100.0,
            grade="A",
            is_discriminating=True,
            warnings=[],
            recommendations=[],
        )
        
        d = result.to_dict()
        
        assert d["position_score"] == 100.0
        assert d["grade"] == "A"
        assert d["is_discriminating"] == True


class TestAlleleScoring:
    """Test allele discrimination scoring."""
    
    def test_3prime_terminal_transversion(self):
        """Test best case: SNP at 3' terminal with transversion."""
        result = score_allele_discrimination(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=0,  # 3' terminal
            ref_allele="A",
            alt_allele="T",  # Transversion
        )
        
        assert result.position_score == 100.0
        assert result.mismatch_score == 100.0
        assert result.grade == "A"
        assert result.is_discriminating == True
    
    def test_3prime_terminal_transition(self):
        """Test SNP at 3' terminal with transition (less optimal)."""
        result = score_allele_discrimination(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=0,
            ref_allele="A",
            alt_allele="G",  # Transition
        )
        
        assert result.mismatch_score < 100.0  # Transition penalty
        assert "transition" in result.warnings[0].lower()
    
    def test_internal_snp_poor_discrimination(self):
        """Test SNP at internal position (poor discrimination)."""
        result = score_allele_discrimination(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=5,  # Internal
            ref_allele="A",
            alt_allele="T",
        )
        
        assert result.position_score < 50.0
        assert result.is_discriminating == False
        assert any("poor" in w.lower() for w in result.warnings)
    
    def test_3prime_minus_1(self):
        """Test SNP at 3'-1 position."""
        result = score_allele_discrimination(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=1,  # 3'-1
            ref_allele="A",
            alt_allele="T",
        )
        
        assert result.position_score == 70.0
        assert result.is_discriminating == True


class TestSnpPosition:
    """Test SNP position validation."""
    
    def test_validate_3prime_terminal(self):
        """Test 3' terminal position is valid."""
        primer = "ATGCGATCGATCGATCGA"
        # SNP at 3' terminal = index 17 (0-indexed from 5')
        assert validate_snp_position(primer, 17) == True
    
    def test_validate_internal_invalid(self):
        """Test internal position may be invalid."""
        primer = "ATGCGATCGATCGATCGA"
        # SNP at middle = poor discrimination
        assert validate_snp_position(primer, 5, max_distance_from_3prime=2) == False
    
    def test_analyze_snp_context(self):
        """Test SNP context analysis."""
        primer = "ATGCGATCGATCGATCGA"
        result = analyze_snp_context(primer, 17)  # 3' terminal
        
        assert result.is_optimal == True
        assert result.snp_from_3prime == 0
        assert result.snp_base == "A"
    
    def test_analyze_snp_context_internal(self):
        """Test internal SNP context."""
        primer = "ATGCGATCGATCGATCGA"
        result = analyze_snp_context(primer, 8)  # Middle
        
        assert result.is_optimal == False
        assert result.is_acceptable == False
        assert len(result.warnings) > 0


class TestDiscriminationTm:
    """Test Tm discrimination calculations."""
    
    def test_calculate_tm_difference(self):
        """Test Tm calculation returns tuple."""
        tm_matched, tm_mismatched, delta_tm = calculate_discrimination_tm(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=17,  # 3' terminal
            ref_allele="A",
            alt_allele="T",
        )
        
        assert tm_matched > 0
        assert tm_mismatched < tm_matched  # Mismatch lowers Tm
        assert delta_tm > 0
    
    def test_3prime_mismatch_higher_delta(self):
        """Test 3' mismatch gives higher delta Tm."""
        _, _, delta_3prime = calculate_discrimination_tm(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=17,  # 3' terminal
            ref_allele="A",
            alt_allele="T",
        )
        
        _, _, delta_internal = calculate_discrimination_tm(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=8,  # Internal
            ref_allele="A",
            alt_allele="T",
        )
        
        assert delta_3prime > delta_internal
    
    def test_estimate_specificity_excellent(self):
        """Test excellent specificity classification."""
        result = estimate_allele_specificity(delta_tm=10.0)
        
        assert result["specificity"] == "Excellent"
        assert result["score"] == 100
    
    def test_estimate_specificity_poor(self):
        """Test poor specificity classification."""
        result = estimate_allele_specificity(delta_tm=1.0)
        
        assert result["specificity"] == "Poor"
        assert result["score"] == 40


class TestGenotypingAPI:
    """Test genotyping API function."""
    
    def test_api_basic(self):
        """Test basic API call."""
        from primerlab.api import score_genotyping_primer_api
        
        result = score_genotyping_primer_api(
            primer_sequence="ATGCGATCGATCGATCGA",
            snp_position=0,  # 3' terminal
            ref_allele="A",
            alt_allele="T",
        )
        
        assert "combined_score" in result
        assert "grade" in result
        assert "tm_matched" in result
        assert "delta_tm" in result
        assert "specificity" in result
    
    def test_api_optimal_case(self):
        """Test API with optimal SNP."""
        from primerlab.api import score_genotyping_primer_api
        
        result = score_genotyping_primer_api(
            primer_sequence="ATGCGATCGATCGATCGT",
            snp_position=0,
            ref_allele="T",
            alt_allele="A",
        )
        
        assert result["is_discriminating"] == True
        assert result["grade"] in ["A", "B"]
