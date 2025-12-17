"""
Unit tests for In-silico PCR Engine (v0.2.0)

Tests virtual PCR simulation, binding detection, and product prediction.
"""

import pytest
from primerlab.core.insilico.engine import (
    InsilicoPCR,
    run_insilico_pcr,
    reverse_complement,
    calculate_match_percent,
    find_binding_sites,
    predict_products,
    PrimerBinding,
    AmpliconPrediction,
    InsilicoPCRResult,
    DEFAULT_INSILICO_PARAMS
)
from primerlab.core.insilico.binding import (
    analyze_binding,
    find_all_binding_sites,
    calculate_three_prime_dg,
    BindingSite
)


# Test fixtures
TEMPLATE_SEQ = (
    "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGTTGTCCCAATTCTTGTTGAATTAGATGGTGATGTTAATGGGCACA"
    "AATTTTCTGTCAGTGGAGAGGGTGAAGGTGATGCAACATACGGAAAACTTACCCTTAAATTTATTTGCACTACTGG"
    "AAAACTACCTGTTCCATGGCCAACACTTGTCACTACTTTCTCTTATGGTGTTCAATGCTTTTCCCGTTATCCGGAT"
    "CACATGAAACGGCATGACTTTTTCAAGAGTGCCATGCCCGAAGGTTATGTACAGGAACGCACTATATCTTTCAAAG"
    "ATGACGGGAACTACAAGACGCGTGCTGAAGTCAAGTTTGAAGGTGATACCCTTGTTAATCGTATCGAGTTAAAAGG"
    "TATTGATTTTAAAGAAGATGGAAACATTCTCGGACACAAACTCGAGTACAACTATAACTCACACAATGTATACATC"
    "ACGGCAGACAAACAAAAGAATGGAATCAAAGCTAACTTCAAAATTCGCCACAACATTGAAGATGGATCCGTTCAAC"
    "TAGCAGACCATTATCAACAAAATACTCCAATTGGCGATGGCCCTGTCCTTTTACCAGACAACCATTACCTGTCGAC"
    "ACAATCTGCCCTTTCGAAAGATCCCAACGAAAAGCGTGACCACATGGTCCTTCTTGAGTTTGTAACTGCTGCTGGG"
)

# Perfect match primers for this template (GFP)
FORWARD_PRIMER = "ATGAGTAAAGGAGAAGAACTTTTC"  # Matches start
REVERSE_PRIMER = "CAGCAGTTACAAACTCAAGAAGG"   # Reverse complement of end region


class TestReverseComplement:
    """Tests for reverse complement function."""
    
    def test_simple_sequence(self):
        assert reverse_complement("ATGC") == "GCAT"
    
    def test_palindrome(self):
        assert reverse_complement("GAATTC") == "GAATTC"  # EcoRI site
    
    def test_with_n(self):
        assert reverse_complement("ATNG") == "CNAT"
    
    def test_lowercase(self):
        assert reverse_complement("atgc") == "gcat"


class TestMatchCalculation:
    """Tests for match percentage calculation."""
    
    def test_perfect_match(self):
        pct, mm, three_p = calculate_match_percent("ATGCAT", "ATGCAT")
        assert pct == 100.0
        assert mm == 0
        assert three_p == 6
    
    def test_one_mismatch(self):
        pct, mm, three_p = calculate_match_percent("ATGCAT", "ATGCTT")
        assert pct == pytest.approx(83.33, rel=0.1)
        assert mm == 1
        assert three_p == 1  # Only last T matches
    
    def test_3prime_mismatch(self):
        pct, mm, three_p = calculate_match_percent("ATGCAT", "ATGCAG")
        assert three_p == 0  # Last base differs
    
    def test_5prime_mismatch(self):
        pct, mm, three_p = calculate_match_percent("ATGCAT", "GTGCAT")
        assert three_p == 5  # Last 5 match, first differs


class TestFindBindingSites:
    """Tests for binding site detection."""
    
    def test_perfect_match_forward(self):
        """Should find perfect match at start of template."""
        bindings = find_binding_sites(
            primer_seq=FORWARD_PRIMER,
            template_seq=TEMPLATE_SEQ,
            primer_name="Forward",
            strand='+',
            params=DEFAULT_INSILICO_PARAMS
        )
        assert len(bindings) >= 1
        assert bindings[0].position == 0
        assert bindings[0].match_percent == 100.0
        assert bindings[0].is_valid == True
    
    def test_no_binding(self):
        """Should return empty for non-matching primer."""
        bindings = find_binding_sites(
            primer_seq="NNNNNNNNNNNNNNNN",  # Won't match anything
            template_seq=TEMPLATE_SEQ,
            primer_name="Fake",
            strand='+',
            params=DEFAULT_INSILICO_PARAMS
        )
        assert len(bindings) == 0
    
    def test_reverse_strand_binding(self):
        """Should find reverse primer on - strand."""
        bindings = find_binding_sites(
            primer_seq=REVERSE_PRIMER,
            template_seq=TEMPLATE_SEQ,
            primer_name="Reverse",
            strand='-',
            params=DEFAULT_INSILICO_PARAMS
        )
        # Should find at least one binding
        assert len(bindings) >= 1


class TestInsilicoPCR:
    """Tests for complete in-silico PCR simulation."""
    
    def test_basic_run(self):
        """Basic run should find products."""
        result = run_insilico_pcr(
            template=TEMPLATE_SEQ,
            forward_primer=FORWARD_PRIMER,
            reverse_primer=REVERSE_PRIMER,
            template_name="GFP"
        )
        assert isinstance(result, InsilicoPCRResult)
        assert result.template_name == "GFP"
        assert result.template_length == len(TEMPLATE_SEQ)
    
    def test_engine_class(self):
        """InsilicoPCR class should work."""
        engine = InsilicoPCR()
        result = engine.run(
            template=TEMPLATE_SEQ,
            forward_primer=FORWARD_PRIMER,
            reverse_primer=REVERSE_PRIMER
        )
        assert isinstance(result, InsilicoPCRResult)
    
    def test_custom_params(self):
        """Custom parameters should be applied."""
        custom_params = {
            "min_3prime_match": 5,
            "product_size_max": 1000
        }
        engine = InsilicoPCR(params=custom_params)
        assert engine.params["min_3prime_match"] == 5
        assert engine.params["product_size_max"] == 1000
        # Defaults should still be there
        assert engine.params["na_conc"] == 50
    
    def test_short_template_error(self):
        """Should error on template < 50bp."""
        result = run_insilico_pcr(
            template="ATGCAT",
            forward_primer="ATGCAT",
            reverse_primer="ATGCAT"
        )
        assert result.success == False
        assert len(result.errors) > 0
    
    def test_no_binding_warning(self):
        """Should warn when no binding found."""
        result = run_insilico_pcr(
            template=TEMPLATE_SEQ,
            forward_primer="NNNNNNNNNNNNNNNNNNNN",  # Won't bind
            reverse_primer="NNNNNNNNNNNNNNNNNNNN"
        )
        assert result.success == False
        assert len(result.warnings) > 0


class TestBindingAnalysis:
    """Tests for binding.py module."""
    
    def test_analyze_binding_perfect(self):
        """Perfect match should be valid."""
        primer = "ATGAGTAAAG"
        target = "ATGAGTAAAG"
        
        site = analyze_binding(
            primer_seq=primer,
            target_seq=target,
            position=0,
            strand='+'
        )
        
        assert site.match_percent == 100.0
        assert site.mismatch_count == 0
        assert site.three_prime_match == len(primer)
        assert site.is_valid == True
    
    def test_analyze_binding_mismatch(self):
        """Should detect mismatches correctly."""
        primer = "ATGAGTAAAG"
        target = "ATGAGTTTAG"  # 2 mismatches in middle
        
        site = analyze_binding(
            primer_seq=primer,
            target_seq=target,
            position=0,
            strand='+'
        )
        
        assert site.mismatch_count == 2
        assert site.match_percent == 80.0
    
    def test_three_prime_dg_calculation(self):
        """ΔG should be calculated."""
        dg = calculate_three_prime_dg("ATGCA", "ATGCA")
        assert isinstance(dg, float)
        assert dg < 0  # Should be negative (stable)
    
    def test_find_all_binding_sites(self):
        """Should find all sites above threshold."""
        sites = find_all_binding_sites(
            primer_seq=FORWARD_PRIMER,
            template_seq=TEMPLATE_SEQ,
            strand='+'
        )
        assert len(sites) >= 1
        assert all(isinstance(s, BindingSite) for s in sites)


class TestProductPrediction:
    """Tests for product prediction."""
    
    def test_product_size_calculation(self):
        """Product size should be calculated correctly."""
        # Create mock bindings
        fwd = PrimerBinding(
            primer_name="Forward",
            primer_seq="ATGCAT",
            strand='+',
            position=10,
            match_percent=100,
            mismatches=0,
            three_prime_match=6,
            binding_tm=60,
            is_valid=True
        )
        rev = PrimerBinding(
            primer_name="Reverse",
            primer_seq="ATGCAT",
            strand='-',
            position=200,  # End position for reverse
            match_percent=100,
            mismatches=0,
            three_prime_match=6,
            binding_tm=60,
            is_valid=True
        )
        
        products = predict_products(
            forward_bindings=[fwd],
            reverse_bindings=[rev],
            template_seq=TEMPLATE_SEQ,
            params=DEFAULT_INSILICO_PARAMS
        )
        
        if products:
            assert products[0].product_size == 196  # 206 - 10


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_very_long_template(self):
        """Should handle long templates."""
        long_template = TEMPLATE_SEQ * 10  # ~7000bp
        result = run_insilico_pcr(
            template=long_template,
            forward_primer=FORWARD_PRIMER,
            reverse_primer=REVERSE_PRIMER
        )
        assert isinstance(result, InsilicoPCRResult)
    
    def test_lowercase_template(self):
        """Should handle lowercase sequences."""
        result = run_insilico_pcr(
            template=TEMPLATE_SEQ.lower(),
            forward_primer=FORWARD_PRIMER.lower(),
            reverse_primer=REVERSE_PRIMER.lower()
        )
        assert isinstance(result, InsilicoPCRResult)
    
    def test_n_in_sequence(self):
        """Should handle N bases in sequence."""
        template_with_n = TEMPLATE_SEQ[:50] + "NNNNN" + TEMPLATE_SEQ[55:]
        result = run_insilico_pcr(
            template=template_with_n,
            forward_primer=FORWARD_PRIMER,
            reverse_primer=REVERSE_PRIMER
        )
        assert isinstance(result, InsilicoPCRResult)
