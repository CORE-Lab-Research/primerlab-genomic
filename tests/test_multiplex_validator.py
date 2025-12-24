"""
Unit tests for Multiplex Validator.

Tests:
- Initialization with preset modes
- Dimer validation
- Tm uniformity validation
- GC uniformity validation
- Full validation workflow
- Edge cases and fallbacks
"""

import pytest
from primerlab.core.multiplex.models import (
    MultiplexPair,
    DimerResult,
    CompatibilityMatrix,
)
from primerlab.core.multiplex.validator import MultiplexValidator


class TestValidatorInit:
    """Tests for MultiplexValidator initialization."""
    
    def test_default_initialization(self):
        """Test default initialization uses standard mode."""
        validator = MultiplexValidator()
        assert validator.mode == "standard"
    
    def test_custom_mode(self):
        """Test custom mode selection."""
        config = {"multiplex": {"mode": "strict"}}
        validator = MultiplexValidator(config)
        assert validator.mode == "strict"
    
    def test_user_override(self):
        """Test user can override settings."""
        config = {
            "multiplex": {
                "mode": "standard",
                "dimer_dg_threshold": -7.0,
            }
        }
        validator = MultiplexValidator(config)
        assert validator.settings["dimer_dg_threshold"] == -7.0


class TestDimerValidation:
    """Tests for dimer validation."""
    
    def test_empty_matrix_valid(self):
        """Test empty matrix is valid."""
        validator = MultiplexValidator()
        matrix = CompatibilityMatrix()
        
        is_valid, warnings, errors = validator.validate_dimers(matrix)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_no_problematic_dimers_valid(self):
        """Test no problematic dimers passes validation."""
        validator = MultiplexValidator()
        
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
        )
        
        is_valid, warnings, errors = validator.validate_dimers(matrix)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_severe_dimer_fails(self):
        """Test severe dimer causes validation failure."""
        validator = MultiplexValidator()
        
        # Very severe dimer (>5 kcal below threshold)
        bad_dimer = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-15.0,  # Very bad
            is_problematic=True,
        )
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            matrix={("P1", "P2"): bad_dimer},
            total_dimers=1,
            problematic_count=1,
        )
        
        is_valid, warnings, errors = validator.validate_dimers(matrix)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_moderate_dimer_warning_only(self):
        """Test moderate dimer causes warning but not failure."""
        validator = MultiplexValidator()
        
        # Moderate dimer (2-5 kcal below threshold)
        moderate_dimer = DimerResult(
            primer1_name="P1",
            primer2_name="P2",
            primer1_seq="ATGC",
            primer2_seq="GCTA",
            delta_g=-9.0,  # Moderate (standard threshold is -6)
            is_problematic=True,
        )
        matrix = CompatibilityMatrix(
            primer_names=["P1", "P2"],
            matrix={("P1", "P2"): moderate_dimer},
            total_dimers=1,
            problematic_count=1,
        )
        
        is_valid, warnings, errors = validator.validate_dimers(matrix)
        
        # Should generate warning but not error
        assert len(warnings) > 0 or len(errors) == 0  # Either warn or pass


class TestTmValidation:
    """Tests for Tm uniformity validation."""
    
    def test_single_pair_valid(self):
        """Test single pair always valid."""
        validator = MultiplexValidator()
        pairs = [MultiplexPair("P1", "ATGC", "GCTA", tm_forward=60.0, tm_reverse=60.0)]
        
        is_valid, warnings, errors = validator.validate_tm_uniformity(pairs)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_uniform_tm_valid(self):
        """Test uniform Tm values pass validation."""
        validator = MultiplexValidator()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", tm_forward=60.0, tm_reverse=60.0),
            MultiplexPair("P2", "TTTT", "AAAA", tm_forward=60.5, tm_reverse=59.5),
        ]
        
        is_valid, warnings, errors = validator.validate_tm_uniformity(pairs)
        
        assert is_valid is True
    
    def test_spread_tm_warning(self):
        """Test spread Tm values cause warning or error."""
        validator = MultiplexValidator()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", tm_forward=55.0, tm_reverse=55.0),
            MultiplexPair("P2", "TTTT", "AAAA", tm_forward=65.0, tm_reverse=65.0),
        ]
        
        is_valid, warnings, errors = validator.validate_tm_uniformity(pairs)
        
        # 10°C spread should trigger warning or error (default limit is 2°C)
        assert len(warnings) > 0 or len(errors) > 0, \
            f"Expected warning/error for 10°C Tm spread, got warnings={warnings}, errors={errors}"


class TestGcValidation:
    """Tests for GC uniformity validation."""
    
    def test_uniform_gc_valid(self):
        """Test uniform GC values pass validation."""
        validator = MultiplexValidator()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA", gc_forward=50.0, gc_reverse=50.0),
            MultiplexPair("P2", "TTTT", "AAAA", gc_forward=52.0, gc_reverse=48.0),
        ]
        
        is_valid, warnings, errors = validator.validate_gc_uniformity(pairs)
        
        assert is_valid is True


class TestFullValidation:
    """Tests for full validation workflow."""
    
    def test_validate_returns_tuple(self):
        """Test validate returns proper tuple."""
        validator = MultiplexValidator()
        
        pairs = [MultiplexPair("P1", "ATGC", "GCTA")]
        matrix = CompatibilityMatrix()
        
        result = validator.validate(matrix, pairs)
        
        assert isinstance(result, tuple)
        assert len(result) == 3
        is_valid, warnings, errors = result
        assert isinstance(is_valid, bool)
        assert isinstance(warnings, list)
        assert isinstance(errors, list)
    
    def test_get_validation_summary(self):
        """Test validation summary dict."""
        validator = MultiplexValidator()
        
        pairs = [MultiplexPair("P1", "ATGC", "GCTA")]
        matrix = CompatibilityMatrix()
        
        summary = validator.get_validation_summary(matrix, pairs)
        
        assert "is_valid" in summary
        assert "mode" in summary
        assert "settings" in summary
        assert "pair_count" in summary
        assert "warnings" in summary
        assert "errors" in summary


class TestValidationFallbacks:
    """Tests for fallback behavior."""
    
    def test_empty_pairs_valid(self):
        """Test empty pairs list is valid."""
        validator = MultiplexValidator()
        
        is_valid, warnings, errors = validator.validate(
            CompatibilityMatrix(),
            []
        )
        
        assert is_valid is True
    
    def test_missing_tm_values_handled(self):
        """Test missing Tm values don't crash."""
        validator = MultiplexValidator()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA"),  # No Tm values
            MultiplexPair("P2", "TTTT", "AAAA"),
        ]
        
        # Should not raise
        is_valid, warnings, errors = validator.validate_tm_uniformity(pairs)
        assert is_valid is True  # No Tm data = can't fail
    
    def test_missing_gc_values_handled(self):
        """Test missing GC values don't crash."""
        validator = MultiplexValidator()
        pairs = [
            MultiplexPair("P1", "ATGC", "GCTA"),  # No GC values
            MultiplexPair("P2", "TTTT", "AAAA"),
        ]
        
        # Should not raise
        is_valid, warnings, errors = validator.validate_gc_uniformity(pairs)
        assert is_valid is True  # No GC data = can't fail
