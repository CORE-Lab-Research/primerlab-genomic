"""
Tests for Phase 3 parameter validation in config_validator.py.
Covers Tasks 3.1-3.10 of the Primer3 Full Coverage development plan.
"""
import pytest
from primerlab.core.config_validator import validate_config, ConfigValidator


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _cfg(**params):
    """Return a minimal config dict with given parameters."""
    return {"sequence": "ATCG", "parameters": dict(params)}


def _thermo_cfg(**thermo):
    """Return a minimal config dict with given thermodynamics sub-section."""
    return {"sequence": "ATCG", "parameters": {"thermodynamics": dict(thermo)}}


# ===========================================================================
# TASK 1.3 — Thermodynamics section (regression guard)
# ===========================================================================

def test_valid_thermo_config():
    """Valid thermodynamics config should pass with no errors."""
    config = {
        "sequence": "ATCG",
        "workflow": "pcr",
        "output": {"directory": "out"},
        "parameters": {
            "thermodynamics": {
                "salt_monovalent": 50.0,
                "salt_divalent": 1.5,
                "tm_method": "santalucia",
                "salt_corrections": "santalucia",
            }
        },
    }
    result = validate_config(config)
    assert result.valid is True
    assert len(result.errors) == 0


def test_invalid_tm_method():
    result = validate_config(_thermo_cfg(tm_method="invalid_method"))
    assert result.valid is False
    assert any("Invalid tm_method" in e.message for e in result.errors)


def test_invalid_salt_corrections():
    result = validate_config(_thermo_cfg(salt_corrections="invalid_salt"))
    assert result.valid is False
    assert any("Invalid salt_corrections" in e.message for e in result.errors)


def test_numeric_type_validation():
    result = validate_config(_thermo_cfg(salt_monovalent="high"))
    assert result.valid is False
    assert any("must be a number" in e.message for e in result.errors)


def test_range_warning():
    result = validate_config(_thermo_cfg(salt_monovalent=2000.0))
    assert result.valid is True  # warning, not error
    assert any("outside typical range" in w.message for w in result.warnings)


# ===========================================================================
# TASK 3.1 — max_poly_x
# ===========================================================================

def test_max_poly_x_valid():
    """max_poly_x = 4 is a valid non-negative integer."""
    result = validate_config(_cfg(max_poly_x=4))
    assert result.valid is True
    assert not any("max_poly_x" in e.message for e in result.errors)


def test_max_poly_x_zero_valid():
    """max_poly_x = 0 means no mononucleotide runs allowed — still valid."""
    result = validate_config(_cfg(max_poly_x=0))
    assert result.valid is True


def test_max_poly_x_invalid_negative():
    result = validate_config(_cfg(max_poly_x=-1))
    assert result.valid is False
    assert any("max_poly_x" in e.message for e in result.errors)


def test_max_poly_x_invalid_float():
    result = validate_config(_cfg(max_poly_x=3.5))
    assert result.valid is False
    assert any("max_poly_x" in e.message for e in result.errors)


def test_max_poly_x_invalid_bool():
    """True is technically int in Python, but we treat it as invalid."""
    result = validate_config(_cfg(max_poly_x=True))
    assert result.valid is False


# ===========================================================================
# TASK 3.2 — max_ns
# ===========================================================================

def test_max_ns_valid():
    result = validate_config(_cfg(max_ns=0))
    assert result.valid is True


def test_max_ns_valid_nonzero():
    result = validate_config(_cfg(max_ns=2))
    assert result.valid is True


def test_max_ns_invalid_negative():
    result = validate_config(_cfg(max_ns=-1))
    assert result.valid is False
    assert any("max_ns" in e.message for e in result.errors)


def test_max_ns_invalid_float():
    result = validate_config(_cfg(max_ns=1.5))
    assert result.valid is False


# ===========================================================================
# TASK 3.3 — max_tm_diff
# ===========================================================================

def test_max_tm_diff_valid():
    result = validate_config(_cfg(max_tm_diff=5.0))
    assert result.valid is True


def test_max_tm_diff_zero_valid():
    """max_tm_diff=0 means primer pair must have identical Tm — valid constraint."""
    result = validate_config(_cfg(max_tm_diff=0))
    assert result.valid is True


def test_max_tm_diff_invalid_string():
    result = validate_config(_cfg(max_tm_diff="five"))
    assert result.valid is False
    assert any("max_tm_diff" in e.message for e in result.errors)


def test_max_tm_diff_invalid_negative():
    result = validate_config(_cfg(max_tm_diff=-1.0))
    assert result.valid is False


# ===========================================================================
# TASK 3.9 — num_candidates
# ===========================================================================

def test_num_candidates_valid():
    result = validate_config(_cfg(num_candidates=50))
    assert result.valid is True


def test_num_candidates_invalid_zero():
    result = validate_config(_cfg(num_candidates=0))
    assert result.valid is False
    assert any("num_candidates" in e.message for e in result.errors)


def test_num_candidates_invalid_string():
    result = validate_config(_cfg(num_candidates="many"))
    assert result.valid is False


# ===========================================================================
# TASK 3.5 — included_region
# ===========================================================================

def test_included_region_valid():
    result = validate_config(_cfg(included_region={"start": 100, "length": 500}))
    assert result.valid is True


def test_included_region_missing_start():
    result = validate_config(_cfg(included_region={"length": 500}))
    assert result.valid is False
    assert any("start" in e.message for e in result.errors)


def test_included_region_missing_length():
    result = validate_config(_cfg(included_region={"start": 100}))
    assert result.valid is False
    assert any("length" in e.message for e in result.errors)


def test_included_region_not_dict():
    result = validate_config(_cfg(included_region="100,500"))
    assert result.valid is False
    assert any("included_region" in e.message for e in result.errors)


def test_included_region_negative_start():
    result = validate_config(_cfg(included_region={"start": -1, "length": 500}))
    assert result.valid is False


# ===========================================================================
# TASK 3.6 — Forced positions
# ===========================================================================

def test_force_left_start_valid():
    result = validate_config(_cfg(force_left_start=50))
    assert result.valid is True


def test_force_right_end_valid():
    result = validate_config(_cfg(force_right_end=450))
    assert result.valid is True


def test_force_left_start_invalid_string():
    result = validate_config(_cfg(force_left_start="start"))
    assert result.valid is False
    assert any("force_left_start" in e.message for e in result.errors)


def test_force_positions_invalid_negative():
    result = validate_config(_cfg(force_right_start=-10))
    assert result.valid is False


def test_force_positions_all_valid():
    """All four forced position keys provided simultaneously."""
    result = validate_config(_cfg(
        force_left_start=50,
        force_left_end=70,
        force_right_start=450,
        force_right_end=470,
    ))
    assert result.valid is True


# ===========================================================================
# TASK 3.7 — must_match constraints
# ===========================================================================

def test_must_match_five_prime_valid():
    result = validate_config(_cfg(must_match_five_prime="NNNNN"))
    assert result.valid is True


def test_must_match_three_prime_valid():
    result = validate_config(_cfg(must_match_three_prime="NNNNG"))
    assert result.valid is True


def test_must_match_five_prime_invalid_not_string():
    result = validate_config(_cfg(must_match_five_prime=12345))
    assert result.valid is False
    assert any("must_match_five_prime" in e.message for e in result.errors)


def test_must_match_three_prime_invalid_characters():
    result = validate_config(_cfg(must_match_three_prime="XXXXX"))
    assert result.valid is False
    assert any("invalid characters" in e.message for e in result.errors)


def test_must_match_both_valid():
    result = validate_config(_cfg(
        must_match_five_prime="NNANN",
        must_match_three_prime="NNNNG",
    ))
    assert result.valid is True


# ===========================================================================
# TASK 3.8 — qc_method
# ===========================================================================

def test_qc_method_threshold_valid():
    result = validate_config(_cfg(qc_method="threshold"))
    assert result.valid is True


def test_qc_method_any_valid():
    result = validate_config(_cfg(qc_method="any"))
    assert result.valid is True


def test_qc_method_invalid():
    result = validate_config(_cfg(qc_method="invalid_qc"))
    assert result.valid is False
    assert any("Invalid qc_method" in e.message for e in result.errors)


def test_qc_method_case_insensitive():
    """Validator should normalise case before checking."""
    result = validate_config(_cfg(qc_method="Threshold"))
    assert result.valid is True


def test_qc_method_not_string():
    result = validate_config(_cfg(qc_method=1))
    assert result.valid is False


# ===========================================================================
# TASK 3.10 — weights
# ===========================================================================

def test_weights_valid():
    result = validate_config(_cfg(weights={
        "tm_gt": 1.0, "tm_lt": 1.0,
        "size_gt": 0.5, "size_lt": 0.5,
        "gc_percent_gt": 0.0, "gc_percent_lt": 0.0,
        "end_stability": 0.25,
    }))
    assert result.valid is True


def test_weights_invalid_not_dict():
    result = validate_config(_cfg(weights="not_a_dict"))
    assert result.valid is False
    assert any("weights must be a dictionary" in e.message for e in result.errors)


def test_weights_value_not_number():
    result = validate_config(_cfg(weights={"tm_gt": "high"}))
    assert result.valid is False
    assert any("must be a number" in e.message for e in result.errors)


def test_weights_unknown_key_is_warning():
    """Unknown weight keys should produce a warning, not an error."""
    result = validate_config(_cfg(weights={"unknown_weight": 1.0}))
    assert result.valid is True  # warning only
    assert any("Unknown weight key" in w.message for w in result.warnings)
