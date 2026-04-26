"""
Config Validation (v0.3.3)

Validate PrimerLab configuration files with helpful error messages.
Includes Phase 3 parameter validation (max_poly_x, max_ns, included_region,
forced positions, must_match constraints, qc_method, weights).
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ValidationError:
    """A single validation error."""
    path: str
    message: str
    suggestion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "message": self.message,
            "suggestion": self.suggestion
        }


@dataclass
class ValidationResult:
    """Result of config validation."""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]

    def to_dict(self) -> Dict[str, Any]:
        """Export to dictionary for JSON serialization."""
        return {
            "valid": self.valid,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings]
        }


class ConfigValidator:
    """
    Validate PrimerLab configuration files.
    
    Provides helpful error messages and suggestions.
    """

    # Required fields for each section
    REQUIRED_FIELDS = {
        "sequence": ["sequence", "source"],
        "primers": ["product_size"],
    }

    # Valid values for enum fields
    VALID_VALUES = {
        "primers.gc_clamp": [0, 1, 2, 3],
        "output.format": ["markdown", "json", "csv", "xlsx"],
        "offtarget.mode": ["auto", "blast", "biopython"],
        "thermodynamics.tm_method": ["santalucia", "breslauer"],
        "thermodynamics.salt_corrections": ["santalucia", "schildkraut", "owczarzy"],
        "qc_method": ["threshold", "any"],
    }

    # Type validators (used for thermodynamics section)
    TYPE_VALIDATORS = {
        "primers.tm_opt": (float, int),
        "primers.gc_percent_min": (float, int),
        "offtarget.evalue": (float, int),
        "offtarget.identity": (float, int),
        "offtarget.max_hits": int,
        "thermodynamics.salt_monovalent": (float, int),
        "thermodynamics.salt_divalent": (float, int),
        "thermodynamics.dntp_conc": (float, int),
        "thermodynamics.dna_conc": (float, int),
    }

    def __init__(self):
        """Initialize validator."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate a configuration dictionary.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []

        # Validate required sections
        self._validate_required_sections(config)

        # Validate offtarget section if present
        if "offtarget" in config:
            self._validate_offtarget(config["offtarget"])

        # Validate primers section
        if "primers" in config:
            self._validate_primers(config["primers"])
            
        # Validate thermodynamics section if present
        if "parameters" in config:
            params = config["parameters"]
            if "thermodynamics" in params:
                self._validate_thermodynamics(params["thermodynamics"])
            self._validate_phase3_params(params)

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings
        )

    def _validate_required_sections(self, config: Dict[str, Any]):
        """Validate required sections exist."""
        if "sequence" not in config and "input" not in config:
            self.errors.append(ValidationError(
                path="sequence",
                message="Missing 'sequence' or 'input' section",
                suggestion="Add 'sequence:' section with 'source: file' or inline sequence"
            ))

    def _validate_offtarget(self, offtarget: Dict[str, Any]):
        """Validate offtarget configuration."""
        if offtarget.get("enabled", False):
            # Database is required if enabled
            if not offtarget.get("database"):
                self.errors.append(ValidationError(
                    path="offtarget.database",
                    message="Off-target enabled but no database specified",
                    suggestion="Set 'database: /path/to/genome.fasta'"
                ))
            else:
                db_path = Path(offtarget["database"])
                if not db_path.exists():
                    self.warnings.append(ValidationError(
                        path="offtarget.database",
                        message=f"Database file not found: {db_path}",
                        suggestion="Check the path or use --blast-db to override"
                    ))

        # Validate mode
        if "mode" in offtarget:
            if offtarget["mode"] not in ["auto", "blast", "biopython"]:
                self.errors.append(ValidationError(
                    path="offtarget.mode",
                    message=f"Invalid mode: {offtarget['mode']}",
                    suggestion="Use 'auto', 'blast', or 'biopython'"
                ))

        # Validate numeric fields
        if "evalue" in offtarget:
            if not isinstance(offtarget["evalue"], (int, float)):
                self.errors.append(ValidationError(
                    path="offtarget.evalue",
                    message="E-value must be a number",
                    suggestion="Example: evalue: 10.0"
                ))

        if "identity" in offtarget:
            val = offtarget["identity"]
            if not isinstance(val, (int, float)) or val < 0 or val > 100:
                self.errors.append(ValidationError(
                    path="offtarget.identity",
                    message="Identity must be 0-100",
                    suggestion="Example: identity: 80.0"
                ))

    def _validate_primers(self, primers: Dict[str, Any]):
        """Validate primers configuration."""
        # Validate product_size
        if "product_size" in primers:
            ps = primers["product_size"]
            if isinstance(ps, dict):
                required = ["min", "max"]
                for key in required:
                    if key not in ps:
                        self.warnings.append(ValidationError(
                            path=f"primers.product_size.{key}",
                            message=f"Missing product_size.{key}",
                            suggestion="Add min, opt, max values"
                        ))

        # Validate Tm range
        if "tm_min" in primers and "tm_max" in primers:
            if primers["tm_min"] > primers["tm_max"]:
                self.errors.append(ValidationError(
                    path="primers.tm_min/tm_max",
                    message="tm_min is greater than tm_max",
                    suggestion="Swap the values"
                ))

    def _validate_thermodynamics(self, thermo: Dict[str, Any]):
        """Validate thermodynamics configuration."""
        # Check numeric types and values
        numeric_fields = {
            "salt_monovalent": (0, 1000),
            "salt_divalent": (0, 100),
            "dntp_conc": (0, 10),
            "dna_conc": (0, 10000)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in thermo:
                val = thermo[field]
                if not isinstance(val, (int, float)):
                    self.errors.append(ValidationError(
                        path=f"parameters.thermodynamics.{field}",
                        message=f"{field} must be a number",
                        suggestion=f"Example: {field}: 50.0"
                    ))
                elif not (min_val <= val <= max_val):
                    self.warnings.append(ValidationError(
                        path=f"parameters.thermodynamics.{field}",
                        message=f"{field} value ({val}) is outside typical range ({min_val}-{max_val})",
                        suggestion="Check if the concentration unit is correct"
                    ))
        
        # Check enum fields
        if "tm_method" in thermo:
            if thermo["tm_method"].lower() not in self.VALID_VALUES["thermodynamics.tm_method"]:
                self.errors.append(ValidationError(
                    path="parameters.thermodynamics.tm_method",
                    message=f"Invalid tm_method: {thermo['tm_method']}",
                    suggestion=f"Use one of: {', '.join(self.VALID_VALUES['thermodynamics.tm_method'])}"
                ))
                
        if "salt_corrections" in thermo:
            if thermo["salt_corrections"].lower() not in self.VALID_VALUES["thermodynamics.salt_corrections"]:
                self.errors.append(ValidationError(
                    path="parameters.thermodynamics.salt_corrections",
                    message=f"Invalid salt_corrections: {thermo['salt_corrections']}",
                    suggestion=f"Use one of: {', '.join(self.VALID_VALUES['thermodynamics.salt_corrections'])}"
                ))

    def _validate_phase3_params(self, params: Dict[str, Any]):
        """Validate Phase 3 parameters (max_poly_x, max_ns, max_tm_diff,
        num_candidates, included_region, forced positions, must_match, weights, qc_method)."""

        # --- Task 3.1: Poly-X ---
        if "max_poly_x" in params:
            val = params["max_poly_x"]
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                self.errors.append(ValidationError(
                    path="parameters.max_poly_x",
                    message="max_poly_x must be a non-negative integer",
                    suggestion="Example: max_poly_x: 4"
                ))

        # --- Task 3.2: Max Ns ---
        if "max_ns" in params:
            val = params["max_ns"]
            if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                self.errors.append(ValidationError(
                    path="parameters.max_ns",
                    message="max_ns must be a non-negative integer",
                    suggestion="Example: max_ns: 0"
                ))

        # --- Task 3.3: Max Tm Diff ---
        if "max_tm_diff" in params:
            val = params["max_tm_diff"]
            if not isinstance(val, (int, float)) or isinstance(val, bool) or val < 0:
                self.errors.append(ValidationError(
                    path="parameters.max_tm_diff",
                    message="max_tm_diff must be a non-negative number (°C)",
                    suggestion="Example: max_tm_diff: 5.0"
                ))

        # --- Task 3.9: Num Candidates ---
        if "num_candidates" in params:
            val = params["num_candidates"]
            if not isinstance(val, int) or isinstance(val, bool) or val <= 0:
                self.errors.append(ValidationError(
                    path="parameters.num_candidates",
                    message="num_candidates must be a positive integer",
                    suggestion="Example: num_candidates: 50"
                ))

        # --- Task 3.5: Included Region ---
        if "included_region" in params:
            ir = params["included_region"]
            if not isinstance(ir, dict):
                self.errors.append(ValidationError(
                    path="parameters.included_region",
                    message="included_region must be a dict with 'start' and 'length' keys",
                    suggestion="Example: included_region: { start: 100, length: 500 }"
                ))
            else:
                for key in ["start", "length"]:
                    if key not in ir:
                        self.errors.append(ValidationError(
                            path=f"parameters.included_region.{key}",
                            message=f"included_region is missing required key: '{key}'",
                            suggestion="included_region requires both 'start' and 'length'"
                        ))
                    elif not isinstance(ir[key], int) or isinstance(ir[key], bool) or ir[key] < 0:
                        self.errors.append(ValidationError(
                            path=f"parameters.included_region.{key}",
                            message=f"included_region.{key} must be a non-negative integer",
                            suggestion=f"Example: {key}: 0"
                        ))

        # --- Task 3.6: Forced Positions ---
        forced_pos_keys = [
            "force_left_start", "force_left_end",
            "force_right_start", "force_right_end"
        ]
        for key in forced_pos_keys:
            if key in params:
                val = params[key]
                if not isinstance(val, int) or isinstance(val, bool) or val < 0:
                    self.errors.append(ValidationError(
                        path=f"parameters.{key}",
                        message=f"{key} must be a non-negative integer (0-based position)",
                        suggestion=f"Example: {key}: 50"
                    ))

        # --- Task 3.7: Must-Match Constraints ---
        match_keys = ["must_match_five_prime", "must_match_three_prime"]
        valid_iupac = set("NACGTRYSWKMBDHVnacgtrysWkmbdhv")
        for key in match_keys:
            if key in params:
                val = params[key]
                if not isinstance(val, str):
                    self.errors.append(ValidationError(
                        path=f"parameters.{key}",
                        message=f"{key} must be a string pattern (e.g. 'NNNNG')",
                        suggestion="Use IUPAC codes: N=any, R=A/G, Y=C/T, etc."
                    ))
                elif not all(c in valid_iupac for c in val):
                    invalid_chars = [c for c in val if c not in valid_iupac]
                    self.errors.append(ValidationError(
                        path=f"parameters.{key}",
                        message=f"{key} contains invalid characters: {invalid_chars}",
                        suggestion="Use only IUPAC characters: A,C,G,T,N,R,Y,S,W,K,M,B,D,H,V"
                    ))

        # --- Task 3.10: Weights ---
        if "weights" in params:
            weights = params["weights"]
            if not isinstance(weights, dict):
                self.errors.append(ValidationError(
                    path="parameters.weights",
                    message="weights must be a dictionary",
                    suggestion="Example: weights: { tm_gt: 1.0, tm_lt: 1.0 }"
                ))
            else:
                valid_weight_keys = {
                    "tm_gt", "tm_lt", "size_gt", "size_lt",
                    "gc_percent_gt", "gc_percent_lt", "end_stability"
                }
                for wk, wv in weights.items():
                    if wk not in valid_weight_keys:
                        self.warnings.append(ValidationError(
                            path=f"parameters.weights.{wk}",
                            message=f"Unknown weight key: '{wk}'",
                            suggestion=f"Valid keys: {', '.join(sorted(valid_weight_keys))}"
                        ))
                    elif not isinstance(wv, (int, float)) or isinstance(wv, bool):
                        self.errors.append(ValidationError(
                            path=f"parameters.weights.{wk}",
                            message=f"Weight '{wk}' must be a number",
                            suggestion="Example: tm_gt: 1.0"
                        ))

        # --- Task 3.8: QC Method ---
        if "qc_method" in params:
            if not isinstance(params["qc_method"], str) or \
               params["qc_method"].lower() not in self.VALID_VALUES["qc_method"]:
                self.errors.append(ValidationError(
                    path="parameters.qc_method",
                    message=f"Invalid qc_method: '{params['qc_method']}'",
                    suggestion=f"Use one of: {', '.join(self.VALID_VALUES['qc_method'])}"
                ))


def validate_config(config: Dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        ValidationResult
    """
    validator = ConfigValidator()
    return validator.validate(config)


def format_validation_errors(result: ValidationResult) -> str:
    """
    Format validation errors for display.
    
    Args:
        result: ValidationResult
        
    Returns:
        Formatted error string
    """
    lines = []

    if result.errors:
        lines.append("❌ Configuration Errors:")
        for err in result.errors:
            lines.append(f"   • {err.path}: {err.message}")
            if err.suggestion:
                lines.append(f"     💡 {err.suggestion}")

    if result.warnings:
        lines.append("\n⚠️  Warnings:")
        for warn in result.warnings:
            lines.append(f"   • {warn.path}: {warn.message}")
            if warn.suggestion:
                lines.append(f"     💡 {warn.suggestion}")

    return "\n".join(lines)
