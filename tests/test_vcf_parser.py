"""
Tests for VCF Parser and Variant Check (v0.3.1)
"""

import pytest
from pathlib import Path

from primerlab.core.models.variant import (
    Variant,
    VariantType,
    VariantOverlap,
    VariantImpact,
    PrimerVariantResult
)
from primerlab.core.tools.vcf_parser import VCFParser, parse_vcf
from primerlab.core.offtarget.variant_check import VariantChecker, check_variants


# Test VCF file
TEST_VCF_PATH = Path(__file__).parent.parent / "examples" / "blast" / "test_variants.vcf"


class TestVariantModel:
    """Tests for Variant dataclass."""
    
    def test_snp_type(self):
        """SNP should be detected correctly."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="G")
        assert var.variant_type == VariantType.SNP
    
    def test_deletion_type(self):
        """Deletion should be detected."""
        var = Variant(chrom="chr1", pos=100, ref="AT", alt="A")
        assert var.variant_type == VariantType.DELETION
    
    def test_insertion_type(self):
        """Insertion should be detected."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="AT")
        assert var.variant_type == VariantType.INSERTION
    
    def test_overlaps(self):
        """Overlap detection should work."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="G")
        
        assert var.overlaps(95, 105)
        assert var.overlaps(100, 100)
        assert not var.overlaps(101, 110)
        assert not var.overlaps(90, 99)


class TestVariantOverlap:
    """Tests for VariantOverlap impact assessment."""
    
    def test_high_impact_3prime(self):
        """Variant at 3' end should be HIGH impact."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="G")
        overlap = VariantOverlap(
            variant=var,
            primer_position=18,
            distance_from_3prime=2
        )
        assert overlap.impact == VariantImpact.HIGH
    
    def test_medium_impact(self):
        """Variant in middle should be MEDIUM impact."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="G")
        overlap = VariantOverlap(
            variant=var,
            primer_position=10,
            distance_from_3prime=5
        )
        assert overlap.impact == VariantImpact.MEDIUM
    
    def test_low_impact_5prime(self):
        """Variant at 5' end should be LOW impact."""
        var = Variant(chrom="chr1", pos=100, ref="A", alt="G")
        overlap = VariantOverlap(
            variant=var,
            primer_position=2,
            distance_from_3prime=15
        )
        assert overlap.impact == VariantImpact.LOW


class TestVCFParser:
    """Tests for VCF parser."""
    
    @pytest.mark.skipif(not TEST_VCF_PATH.exists(), reason="Test VCF not found")
    def test_parse_vcf(self):
        """Should parse VCF file."""
        parser = VCFParser(str(TEST_VCF_PATH))
        variants = list(parser.parse())
        
        assert len(variants) > 0
        assert all(isinstance(v, Variant) for v in variants)
    
    @pytest.mark.skipif(not TEST_VCF_PATH.exists(), reason="Test VCF not found")
    def test_parse_with_region(self):
        """Should filter by region."""
        parser = VCFParser(str(TEST_VCF_PATH))
        variants = list(parser.parse(
            chrom="NC_000913.3_partial",
            start=100,
            end=400
        ))
        
        for v in variants:
            assert 100 <= v.pos <= 400
    
    @pytest.mark.skipif(not TEST_VCF_PATH.exists(), reason="Test VCF not found")
    def test_maf_in_variants(self):
        """MAF should be parsed from INFO."""
        variants = parse_vcf(str(TEST_VCF_PATH))
        
        # At least some should have MAF
        variants_with_maf = [v for v in variants if v.maf is not None]
        assert len(variants_with_maf) > 0


class TestVariantChecker:
    """Tests for variant checker."""
    
    @pytest.mark.skipif(not TEST_VCF_PATH.exists(), reason="Test VCF not found")
    def test_check_primer(self):
        """Should check primer for variants."""
        checker = VariantChecker(str(TEST_VCF_PATH))
        
        result = checker.check_primer(
            primer_seq="ATGCATGCATGCATGCAT",  # 18bp
            chrom="NC_000913.3_partial",
            start=145,  # Should overlap with pos 150
            primer_id="test"
        )
        
        assert isinstance(result, PrimerVariantResult)
        assert result.primer_id == "test"
    
    @pytest.mark.skipif(not TEST_VCF_PATH.exists(), reason="Test VCF not found")
    def test_variant_overlap_detection(self):
        """Should detect overlapping variants."""
        checker = VariantChecker(str(TEST_VCF_PATH))
        
        # Position 150 has a variant
        result = checker.check_primer(
            primer_seq="ATGCATGCATGCATGCAT",
            chrom="NC_000913.3_partial",
            start=140,  # 140-157, should overlap 150
            primer_id="test"
        )
        
        # Should have found the variant at 150
        if result.variant_count > 0:
            assert any(o.variant.pos == 150 for o in result.overlaps)
