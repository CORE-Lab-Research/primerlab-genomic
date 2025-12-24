"""
Multiplex Validation Engine.

Validates multiplex primer sets against configurable thresholds.
Supports preset modes (strict/standard/relaxed) with user overrides.

Version: v0.4.0
"""

from typing import Dict, Any, List, Tuple, Optional
from primerlab.core.logger import get_logger
from primerlab.core.multiplex.models import (
    MultiplexPair,
    CompatibilityMatrix,
)
from primerlab.core.multiplex.scoring import MULTIPLEX_CONFIG

logger = get_logger()


class MultiplexValidator:
    """
    Validates multiplex primer sets against QC thresholds.
    
    Checks:
    - Maximum heterodimer ΔG
    - Tm uniformity (max spread)
    - GC content uniformity
    - Product size overlap (if available)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize validator with configuration.
        
        Args:
            config: Configuration dict with multiplex settings
        """
        config = config or {}
        multiplex_config = config.get("multiplex", {})
        
        # Get mode (default: standard)
        mode = multiplex_config.get("mode", "standard")
        if mode not in MULTIPLEX_CONFIG:
            logger.warning(f"Unknown mode '{mode}', using 'standard'")
            mode = "standard"
        
        # Start with preset settings
        self.settings = MULTIPLEX_CONFIG[mode].copy()
        
        # Apply user overrides
        for key in self.settings:
            if key in multiplex_config:
                self.settings[key] = multiplex_config[key]
        
        self.mode = mode
        logger.debug(f"MultiplexValidator initialized with mode='{mode}'")
    
    def validate_dimers(
        self,
        matrix: CompatibilityMatrix
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate dimer interactions.
        
        Args:
            matrix: Compatibility matrix with dimer results
            
        Returns:
            Tuple of (is_valid, warnings, errors)
        """
        warnings = []
        errors = []
        
        if matrix.total_dimers == 0:
            return True, [], []
        
        threshold = self.settings["dimer_dg_threshold"]
        problematic = matrix.get_problematic_dimers()
        
        for dimer in problematic:
            severity = threshold - dimer.delta_g
            
            if severity > 5.0:
                # Severe - error level
                errors.append(
                    f"Critical dimer: {dimer.primer1_name} + {dimer.primer2_name} "
                    f"(ΔG = {dimer.delta_g:.1f} kcal/mol, threshold = {threshold})"
                )
            elif severity > 2.0:
                # Moderate - warning level
                warnings.append(
                    f"Moderate dimer: {dimer.primer1_name} + {dimer.primer2_name} "
                    f"(ΔG = {dimer.delta_g:.1f} kcal/mol)"
                )
            else:
                # Minor - just log
                logger.debug(
                    f"Minor dimer: {dimer.primer1_name} + {dimer.primer2_name} "
                    f"(ΔG = {dimer.delta_g:.1f})"
                )
        
        is_valid = len(errors) == 0
        return is_valid, warnings, errors
    
    def validate_tm_uniformity(
        self,
        pairs: List[MultiplexPair]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate Tm uniformity across all primers.
        
        Args:
            pairs: List of primer pairs
            
        Returns:
            Tuple of (is_valid, warnings, errors)
        """
        warnings = []
        errors = []
        
        if len(pairs) < 2:
            return True, [], []
        
        # Collect all Tm values
        tm_values = []
        for pair in pairs:
            if pair.tm_forward > 0:
                tm_values.append((f"{pair.name}_F", pair.tm_forward))
            if pair.tm_reverse > 0:
                tm_values.append((f"{pair.name}_R", pair.tm_reverse))
        
        if len(tm_values) < 2:
            return True, [], []
        
        tm_only = [tm for _, tm in tm_values]
        tm_max = max(tm_only)
        tm_min = min(tm_only)
        tm_spread = tm_max - tm_min
        
        tm_diff_max = self.settings["tm_diff_max"]
        
        if tm_spread > tm_diff_max * 2:
            # Severe spread - error
            errors.append(
                f"Tm spread ({tm_spread:.1f}°C) far exceeds limit ({tm_diff_max}°C). "
                f"Range: {tm_min:.1f}°C - {tm_max:.1f}°C"
            )
        elif tm_spread > tm_diff_max:
            # Moderate spread - warning
            warnings.append(
                f"Tm spread ({tm_spread:.1f}°C) exceeds limit ({tm_diff_max}°C). "
                f"Range: {tm_min:.1f}°C - {tm_max:.1f}°C"
            )
        
        is_valid = len(errors) == 0
        return is_valid, warnings, errors
    
    def validate_gc_uniformity(
        self,
        pairs: List[MultiplexPair]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate GC content uniformity across all primers.
        
        Args:
            pairs: List of primer pairs
            
        Returns:
            Tuple of (is_valid, warnings, errors)
        """
        warnings = []
        errors = []
        
        if len(pairs) < 2:
            return True, [], []
        
        # Collect all GC values
        gc_values = []
        for pair in pairs:
            if pair.gc_forward > 0:
                gc_values.append(pair.gc_forward)
            if pair.gc_reverse > 0:
                gc_values.append(pair.gc_reverse)
        
        if len(gc_values) < 2:
            return True, [], []
        
        gc_max = max(gc_values)
        gc_min = min(gc_values)
        gc_spread = gc_max - gc_min
        
        gc_diff_max = self.settings["gc_diff_max"]
        
        if gc_spread > gc_diff_max * 2:
            # Severe spread - error
            errors.append(
                f"GC spread ({gc_spread:.1f}%) far exceeds limit ({gc_diff_max}%). "
                f"Range: {gc_min:.1f}% - {gc_max:.1f}%"
            )
        elif gc_spread > gc_diff_max:
            # Moderate spread - warning
            warnings.append(
                f"GC spread ({gc_spread:.1f}%) exceeds limit ({gc_diff_max}%). "
                f"Range: {gc_min:.1f}% - {gc_max:.1f}%"
            )
        
        is_valid = len(errors) == 0
        return is_valid, warnings, errors
    
    def validate(
        self,
        matrix: CompatibilityMatrix,
        pairs: List[MultiplexPair]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validations on multiplex set.
        
        Args:
            matrix: Compatibility matrix with dimer results
            pairs: List of primer pairs
            
        Returns:
            Tuple of (is_valid, all_warnings, all_errors)
        """
        all_warnings = []
        all_errors = []
        
        # Validate dimers
        dimer_valid, dimer_warn, dimer_err = self.validate_dimers(matrix)
        all_warnings.extend(dimer_warn)
        all_errors.extend(dimer_err)
        
        # Validate Tm uniformity
        tm_valid, tm_warn, tm_err = self.validate_tm_uniformity(pairs)
        all_warnings.extend(tm_warn)
        all_errors.extend(tm_err)
        
        # Validate GC uniformity
        gc_valid, gc_warn, gc_err = self.validate_gc_uniformity(pairs)
        all_warnings.extend(gc_warn)
        all_errors.extend(gc_err)
        
        # Overall validity
        is_valid = dimer_valid and tm_valid and gc_valid
        
        if is_valid:
            logger.info("Multiplex validation passed")
        else:
            logger.warning(f"Multiplex validation failed: {len(all_errors)} errors")
        
        return is_valid, all_warnings, all_errors
    
    def get_validation_summary(
        self,
        matrix: CompatibilityMatrix,
        pairs: List[MultiplexPair]
    ) -> Dict[str, Any]:
        """
        Get detailed validation summary.
        
        Args:
            matrix: Compatibility matrix
            pairs: List of primer pairs
            
        Returns:
            Dictionary with validation details
        """
        is_valid, warnings, errors = self.validate(matrix, pairs)
        
        return {
            "is_valid": is_valid,
            "mode": self.mode,
            "settings": {
                "dimer_dg_threshold": self.settings["dimer_dg_threshold"],
                "tm_diff_max": self.settings["tm_diff_max"],
                "gc_diff_max": self.settings["gc_diff_max"],
            },
            "pair_count": len(pairs),
            "primer_count": len(pairs) * 2,
            "dimer_count": matrix.total_dimers,
            "problematic_dimer_count": matrix.problematic_count,
            "warnings": warnings,
            "errors": errors,
        }
