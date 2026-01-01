"""Tests for New Presets (v0.1.3)."""
import pytest
from pathlib import Path


class TestPresetFilesExist:
    """Test that all preset files exist."""
    
    def test_dna_barcoding_preset_exists(self):
        """DNA barcoding preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "dna_barcoding_default.yaml"
        assert preset_path.exists(), "dna_barcoding_default.yaml not found"
    
    def test_rt_pcr_preset_exists(self):
        """RT-PCR preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "rt_pcr_default.yaml"
        assert preset_path.exists(), "rt_pcr_default.yaml not found"
    
    def test_long_range_preset_exists(self):
        """Long Range preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "long_range_default.yaml"
        assert preset_path.exists(), "long_range_default.yaml not found"


class TestPresetYAMLContent:
    """Test that preset YAML files have required sections."""
    
    def test_dna_barcoding_has_parameters(self):
        """DNA barcoding preset should have parameters section."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "dna_barcoding_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert "parameters" in config
        assert "tm" in config["parameters"]
        assert "product_size_range" in config["parameters"]
    
    def test_rt_pcr_has_parameters(self):
        """RT-PCR preset should have parameters section."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "rt_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert "parameters" in config
        assert "tm" in config["parameters"]
        assert "product_size_range" in config["parameters"]
    
    def test_long_range_has_parameters(self):
        """Long Range preset should have parameters section."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "long_range_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert "parameters" in config
        assert "tm" in config["parameters"]
        assert "product_size_range" in config["parameters"]


class TestPresetQCModes:
    """Test QC mode settings for different presets."""
    
    def test_dna_barcoding_uses_relaxed_qc(self):
        """DNA barcoding should use relaxed QC mode."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "dna_barcoding_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["qc"]["mode"] == "relaxed"
    
    def test_long_range_uses_strict_qc(self):
        """Long Range should use strict QC mode."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "long_range_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["qc"]["mode"] == "strict"
    
    def test_rt_pcr_uses_standard_qc(self):
        """RT-PCR should use standard QC mode."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "rt_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["qc"]["mode"] == "standard"


class TestPresetValues:
    """Test specific values in presets match documentation."""
    
    def test_long_range_product_size(self):
        """Long Range should target 3-10kb amplicons."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "long_range_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["parameters"]["product_size_range"] == "3000-10000"
    
    def test_rt_pcr_product_size(self):
        """RT-PCR should target 80-200bp amplicons."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "rt_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["parameters"]["product_size_range"] == "80-200"
    
    def test_dna_barcoding_product_size(self):
        """DNA barcoding should target 400-700bp amplicons."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "dna_barcoding_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["parameters"]["product_size_range"] == "400-700"


# ================================================
# v0.7.3 New Presets Tests
# ================================================

class TestV073PresetFilesExist:
    """Test that v0.7.3 preset files exist."""
    
    def test_diagnostic_pcr_preset_exists(self):
        """Diagnostic PCR preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "diagnostic_pcr_default.yaml"
        assert preset_path.exists(), "diagnostic_pcr_default.yaml not found"
    
    def test_sequencing_pcr_preset_exists(self):
        """Sequencing PCR preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "sequencing_pcr_default.yaml"
        assert preset_path.exists(), "sequencing_pcr_default.yaml not found"
    
    def test_cloning_pcr_preset_exists(self):
        """Cloning PCR preset file should exist."""
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "cloning_pcr_default.yaml"
        assert preset_path.exists(), "cloning_pcr_default.yaml not found"


class TestV073PresetContent:
    """Test v0.7.3 preset YAML content."""
    
    def test_diagnostic_pcr_content(self):
        """Diagnostic PCR preset should have correct content."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "diagnostic_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["preset"] == "diagnostic_pcr"
        assert config["parameters"]["product_size_range"] == [[80, 200]]
        assert config["qc"]["mode"] == "strict"
        assert "metadata" in config
    
    def test_sequencing_pcr_content(self):
        """Sequencing PCR preset should have correct content."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "sequencing_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["preset"] == "sequencing_pcr"
        assert config["parameters"]["product_size_range"] == [[400, 1000]]
        assert "metadata" in config
    
    def test_cloning_pcr_content(self):
        """Cloning PCR preset should have correct content."""
        import yaml
        preset_path = Path(__file__).parent.parent / "primerlab" / "config" / "cloning_pcr_default.yaml"
        with open(preset_path) as f:
            config = yaml.safe_load(f)
        
        assert config["preset"] == "cloning_pcr"
        assert config["parameters"]["product_size_range"] == [[200, 3000]]
        assert "cloning" in config
        assert "common_sites" in config["cloning"]
    
    def test_all_v073_presets_have_metadata(self):
        """All v0.7.3 presets should have metadata section."""
        import yaml
        presets = [
            "diagnostic_pcr_default.yaml",
            "sequencing_pcr_default.yaml",
            "cloning_pcr_default.yaml",
        ]
        
        for preset_name in presets:
            preset_path = Path(__file__).parent.parent / "primerlab" / "config" / preset_name
            with open(preset_path) as f:
                config = yaml.safe_load(f)
            
            assert "metadata" in config, f"Missing metadata in {preset_name}"
            assert "preset_name" in config["metadata"]
            assert "preset_description" in config["metadata"]
            assert "recommended_for" in config["metadata"]

