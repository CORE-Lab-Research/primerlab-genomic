"""Tests for Region Masking Module (v0.1.6)."""
import pytest
import tempfile
from pathlib import Path


class TestRegionMask:
    """Tests for RegionMask dataclass."""
    
    def test_creation(self):
        """Test RegionMask creation."""
        from primerlab.core.masking import RegionMask
        
        mask = RegionMask(start=10, end=30, reason="repeat")
        
        assert mask.start == 10
        assert mask.end == 30
        assert mask.reason == "repeat"
    
    def test_length_property(self):
        """Test length calculation."""
        from primerlab.core.masking import RegionMask
        
        mask = RegionMask(start=10, end=30, reason="repeat")
        
        assert mask.length == 20
    
    def test_to_primer3_format(self):
        """Test conversion to Primer3 format."""
        from primerlab.core.masking import RegionMask
        
        mask = RegionMask(start=10, end=30, reason="repeat")
        
        primer3_format = mask.to_primer3_format()
        
        assert primer3_format == (10, 20)  # (start, length)


class TestRegionMasker:
    """Tests for RegionMasker class."""
    
    @pytest.fixture
    def masker(self):
        """Create a RegionMasker instance."""
        from primerlab.core.masking import RegionMasker
        return RegionMasker()
    
    def test_detect_lowercase_masks(self, masker):
        """Test lowercase (softmask) detection."""
        # Sequence with lowercase region in middle
        sequence = "ATGCATGCATGCatgcatgcatgcATGCATGCATGC"
        
        masks = masker.detect_lowercase_masks(sequence, min_length=5)
        
        assert len(masks) == 1
        assert masks[0].start == 12
        assert masks[0].end == 24
        assert masks[0].reason == "repeat"
    
    def test_detect_multiple_lowercase_regions(self, masker):
        """Test detection of multiple lowercase regions."""
        sequence = "ATGCatgcatATGCatgcatATGC"
        
        masks = masker.detect_lowercase_masks(sequence, min_length=4)
        
        assert len(masks) == 2
    
    def test_lowercase_min_length_filter(self, masker):
        """Test minimum length filtering."""
        sequence = "ATGCatATGCATGCATGC"  # Only 2bp lowercase
        
        masks = masker.detect_lowercase_masks(sequence, min_length=5)
        
        assert len(masks) == 0
    
    def test_detect_n_masks(self, masker):
        """Test N-masked region detection."""
        sequence = "ATGCATGCNNNNNNNNNNNATGCATGC"
        
        masks = masker.detect_n_masks(sequence, min_length=3)
        
        assert len(masks) == 1
        assert masks[0].reason == "n_masked"
    
    def test_detect_multiple_n_regions(self, masker):
        """Test detection of multiple N regions."""
        sequence = "ATGCNNNNATGCNNNNATGC"
        
        masks = masker.detect_n_masks(sequence, min_length=3)
        
        assert len(masks) == 2
    
    def test_n_mask_min_length(self, masker):
        """Test N mask minimum length filter."""
        sequence = "ATGCNNATGC"  # Only 2 Ns
        
        masks = masker.detect_n_masks(sequence, min_length=3)
        
        assert len(masks) == 0
    
    def test_analyze_sequence_both_types(self, masker):
        """Test combined analysis for both mask types."""
        sequence = "ATGCatgcatNNNNNATGCATGC"
        
        masks = masker.analyze_sequence(
            sequence, 
            detect_lowercase=True,
            detect_n=True,
            min_length=3
        )
        
        assert len(masks) >= 1  # May merge overlapping
    
    def test_merge_overlapping(self, masker):
        """Test overlapping region merging."""
        from primerlab.core.masking import RegionMask
        
        masks = [
            RegionMask(10, 30, "repeat"),
            RegionMask(20, 40, "n_masked"),  # Overlaps with first
            RegionMask(100, 120, "repeat")   # Separate
        ]
        
        merged = masker._merge_overlapping(masks)
        
        assert len(merged) == 2
        assert merged[0].start == 10
        assert merged[0].end == 40  # Extended
    
    def test_add_manual_region(self, masker):
        """Test adding manual excluded region."""
        masker.add_manual_region(100, 150, "user_excluded")
        
        assert len(masker.masks) == 1
        assert masker.masks[0].reason == "user_excluded"
    
    def test_parse_bed_file(self, masker):
        """Test BED file parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bed_path = Path(tmpdir) / "test.bed"
            bed_content = """# Comment line
SEQ1	10	30	repeat
SEQ1	50	70	low_complexity
"""
            bed_path.write_text(bed_content)
            
            masks = masker.parse_bed_file(str(bed_path))
            
            assert len(masks) == 2
            assert masks[0].start == 10
            assert masks[0].end == 30
    
    def test_parse_bed_file_filter_by_name(self, masker):
        """Test BED file parsing with sequence name filter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            bed_path = Path(tmpdir) / "test.bed"
            bed_content = """SEQ1	10	30	repeat
SEQ2	50	70	repeat
SEQ1	100	120	repeat
"""
            bed_path.write_text(bed_content)
            
            masks = masker.parse_bed_file(str(bed_path), seq_name="SEQ1")
            
            assert len(masks) == 2  # Only SEQ1 entries
    
    def test_get_mask_summary(self, masker):
        """Test mask summary generation."""
        from primerlab.core.masking import RegionMask
        
        masks = [
            RegionMask(10, 30, "repeat"),
            RegionMask(50, 70, "repeat"),
            RegionMask(100, 110, "n_masked")
        ]
        
        summary = masker.get_mask_summary(masks, sequence_length=200)
        
        assert summary["total_regions"] == 3
        assert summary["total_masked_bp"] == 50  # 20 + 20 + 10
        assert summary["percent_masked"] == 25.0
        assert "repeat" in summary["by_reason"]


class TestApplyMasksToConfig:
    """Tests for apply_masks_to_config function."""
    
    def test_apply_to_empty_config(self):
        """Test applying masks to config without parameters."""
        from primerlab.core.masking import apply_masks_to_config, RegionMask
        
        config = {"workflow": "pcr"}
        masks = [RegionMask(10, 30, "repeat")]
        
        result = apply_masks_to_config(config, masks)
        
        assert "parameters" in result
        assert "excluded_regions" in result["parameters"]
        assert result["parameters"]["excluded_regions"] == [(10, 20)]
    
    def test_apply_multiple_masks(self):
        """Test applying multiple masks."""
        from primerlab.core.masking import apply_masks_to_config, RegionMask
        
        config = {"workflow": "pcr", "parameters": {}}
        masks = [
            RegionMask(10, 30, "repeat"),
            RegionMask(50, 80, "n_masked")
        ]
        
        result = apply_masks_to_config(config, masks)
        
        assert len(result["parameters"]["excluded_regions"]) == 2
    
    def test_apply_empty_masks(self):
        """Test applying empty masks list."""
        from primerlab.core.masking import apply_masks_to_config
        
        config = {"workflow": "pcr"}
        
        result = apply_masks_to_config(config, [])
        
        assert result == config


class TestFormatMaskReport:
    """Tests for format_mask_report function."""
    
    def test_format_empty(self):
        """Test formatting with no masks."""
        from primerlab.core.masking import format_mask_report
        
        result = format_mask_report([], 1000)
        
        assert "No masked regions" in result
    
    def test_format_with_masks(self):
        """Test formatting with masks."""
        from primerlab.core.masking import format_mask_report, RegionMask
        
        masks = [
            RegionMask(10, 30, "repeat"),
            RegionMask(50, 70, "n_masked")
        ]
        
        result = format_mask_report(masks, 200)
        
        assert "Region Masking Summary" in result
        assert "repeat" in result
        assert "n_masked" in result
