"""
Multiplex Compatibility Scoring Engine.

Calculates overall compatibility score for multiplex primer sets based on:
- Cross-dimer ΔG penalties
- Tm uniformity
- GC content uniformity
- Primer count penalty

Supports preset modes (strict/standard/relaxed) with user-configurable overrides.

Version: v0.4.0
"""

from typing import Dict, Any, List, Tuple, Optional
from statistics import stdev, mean
from primerlab.core.logger import get_logger
from primerlab.core.multiplex.models import (
    MultiplexPair,
    CompatibilityMatrix,
    MultiplexResult,
    score_to_grade,
)

logger = get_logger()


# Mode-specific configurations (following existing PENALTY_CONFIG pattern)
MULTIPLEX_CONFIG = {
    "strict": {
        "dimer_dg_threshold": -5.0,
        "tm_diff_max": 1.5,
        "gc_diff_max": 10.0,
        "dimer_weight": 0.45,
        "tm_weight": 0.25,
        "gc_weight": 0.15,
        "count_weight": 0.15,
        # Penalty factors
        "dimer_penalty_per_kcal": 5.0,   # Points lost per kcal/mol below threshold
        "tm_penalty_per_degree": 10.0,   # Points lost per degree std dev
        "gc_penalty_per_percent": 2.0,   # Points lost per % std dev
        "count_penalty_per_pair": 5.0,   # Points lost per extra pair beyond 2
    },
    "standard": {
        "dimer_dg_threshold": -6.0,
        "tm_diff_max": 2.0,
        "gc_diff_max": 15.0,
        "dimer_weight": 0.40,
        "tm_weight": 0.25,
        "gc_weight": 0.15,
        "count_weight": 0.20,
        "dimer_penalty_per_kcal": 4.0,
        "tm_penalty_per_degree": 8.0,
        "gc_penalty_per_percent": 1.5,
        "count_penalty_per_pair": 4.0,
    },
    "relaxed": {
        "dimer_dg_threshold": -9.0,
        "tm_diff_max": 3.0,
        "gc_diff_max": 20.0,
        "dimer_weight": 0.35,
        "tm_weight": 0.25,
        "gc_weight": 0.15,
        "count_weight": 0.25,
        "dimer_penalty_per_kcal": 3.0,
        "tm_penalty_per_degree": 6.0,
        "gc_penalty_per_percent": 1.0,
        "count_penalty_per_pair": 3.0,
    },
}


class MultiplexScorer:
    """
    Calculates compatibility scores for multiplex primer sets.
    
    Score components:
    - Dimer Score: Based on cross-dimer ΔG values
    - Tm Score: Based on Tm uniformity (std deviation)
    - GC Score: Based on GC content uniformity
    - Count Score: Penalty for large primer sets
    
    Final score is weighted average of components (0-100 scale).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize scorer with configuration.
        
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
        
        # Also check nested 'scoring' section for weights
        scoring_config = multiplex_config.get("scoring", {})
        for key in ["dimer_weight", "tm_weight", "gc_weight", "count_weight"]:
            if key in scoring_config:
                self.settings[key] = scoring_config[key]
        
        self.mode = mode
        logger.debug(f"MultiplexScorer initialized with mode='{mode}'")
    
    def calculate_dimer_score(self, matrix: CompatibilityMatrix) -> Tuple[float, List[str]]:
        """
        Calculate score based on cross-dimer ΔG values.
        
        Args:
            matrix: Compatibility matrix with dimer results
            
        Returns:
            Tuple of (score 0-100, list of warnings)
        """
        warnings = []
        
        if matrix.total_dimers == 0:
            return 100.0, []
        
        threshold = self.settings["dimer_dg_threshold"]
        penalty_per_kcal = self.settings["dimer_penalty_per_kcal"]
        
        total_penalty = 0.0
        problematic_dimers = matrix.get_problematic_dimers()
        
        for dimer in problematic_dimers:
            # Penalty based on how far below threshold
            excess = threshold - dimer.delta_g  # Positive if below threshold
            if excess > 0:
                penalty = excess * penalty_per_kcal
                total_penalty += penalty
                
                if excess > 3.0:  # Severe dimer
                    warnings.append(
                        f"Severe dimer: {dimer.primer1_name} + {dimer.primer2_name} "
                        f"(ΔG = {dimer.delta_g:.1f} kcal/mol)"
                    )
        
        score = max(0.0, 100.0 - total_penalty)
        return score, warnings
    
    def calculate_tm_score(self, pairs: List[MultiplexPair]) -> Tuple[float, List[str]]:
        """
        Calculate score based on Tm uniformity.
        
        Args:
            pairs: List of primer pairs
            
        Returns:
            Tuple of (score 0-100, list of warnings)
        """
        warnings = []
        
        if len(pairs) < 2:
            return 100.0, []
        
        # Collect all Tm values
        tm_values = []
        for pair in pairs:
            if pair.tm_forward > 0:
                tm_values.append(pair.tm_forward)
            if pair.tm_reverse > 0:
                tm_values.append(pair.tm_reverse)
        
        if len(tm_values) < 2:
            return 100.0, []
        
        # Calculate standard deviation
        tm_std = stdev(tm_values)
        tm_max_diff = max(tm_values) - min(tm_values)
        
        penalty_per_degree = self.settings["tm_penalty_per_degree"]
        tm_diff_max = self.settings["tm_diff_max"]
        
        # Penalty based on std deviation
        penalty = tm_std * penalty_per_degree
        score = max(0.0, 100.0 - penalty)
        
        if tm_max_diff > tm_diff_max:
            warnings.append(
                f"Tm spread ({tm_max_diff:.1f}°C) exceeds limit ({tm_diff_max}°C)"
            )
        
        return score, warnings
    
    def calculate_gc_score(self, pairs: List[MultiplexPair]) -> Tuple[float, List[str]]:
        """
        Calculate score based on GC content uniformity.
        
        Args:
            pairs: List of primer pairs
            
        Returns:
            Tuple of (score 0-100, list of warnings)
        """
        warnings = []
        
        if len(pairs) < 2:
            return 100.0, []
        
        # Collect all GC values
        gc_values = []
        for pair in pairs:
            if pair.gc_forward > 0:
                gc_values.append(pair.gc_forward)
            if pair.gc_reverse > 0:
                gc_values.append(pair.gc_reverse)
        
        if len(gc_values) < 2:
            return 100.0, []
        
        # Calculate standard deviation
        gc_std = stdev(gc_values)
        gc_max_diff = max(gc_values) - min(gc_values)
        
        penalty_per_percent = self.settings["gc_penalty_per_percent"]
        gc_diff_max = self.settings["gc_diff_max"]
        
        # Penalty based on std deviation
        penalty = gc_std * penalty_per_percent
        score = max(0.0, 100.0 - penalty)
        
        if gc_max_diff > gc_diff_max:
            warnings.append(
                f"GC spread ({gc_max_diff:.1f}%) exceeds limit ({gc_diff_max}%)"
            )
        
        return score, warnings
    
    def calculate_count_score(self, pair_count: int) -> Tuple[float, List[str]]:
        """
        Calculate score based on number of primer pairs.
        
        More pairs = harder to optimize, so slight penalty.
        
        Args:
            pair_count: Number of primer pairs
            
        Returns:
            Tuple of (score 0-100, list of warnings)
        """
        warnings = []
        
        if pair_count <= 2:
            return 100.0, []
        
        penalty_per_pair = self.settings["count_penalty_per_pair"]
        
        # Penalty for pairs beyond 2
        extra_pairs = pair_count - 2
        penalty = extra_pairs * penalty_per_pair
        score = max(50.0, 100.0 - penalty)  # Floor at 50% for this component
        
        if pair_count > 10:
            warnings.append(
                f"Large multiplex ({pair_count} pairs) may be difficult to optimize"
            )
        
        return score, warnings
    
    def calculate_score(
        self,
        matrix: CompatibilityMatrix,
        pairs: List[MultiplexPair]
    ) -> MultiplexResult:
        """
        Calculate overall compatibility score.
        
        Args:
            matrix: Compatibility matrix with dimer results
            pairs: List of primer pairs
            
        Returns:
            MultiplexResult with score, grade, and recommendations
        """
        all_warnings = []
        recommendations = []
        
        # Calculate component scores
        dimer_score, dimer_warnings = self.calculate_dimer_score(matrix)
        tm_score, tm_warnings = self.calculate_tm_score(pairs)
        gc_score, gc_warnings = self.calculate_gc_score(pairs)
        count_score, count_warnings = self.calculate_count_score(len(pairs))
        
        all_warnings.extend(dimer_warnings)
        all_warnings.extend(tm_warnings)
        all_warnings.extend(gc_warnings)
        all_warnings.extend(count_warnings)
        
        # Weighted average
        weights = {
            "dimer": self.settings["dimer_weight"],
            "tm": self.settings["tm_weight"],
            "gc": self.settings["gc_weight"],
            "count": self.settings["count_weight"],
        }
        
        final_score = (
            dimer_score * weights["dimer"] +
            tm_score * weights["tm"] +
            gc_score * weights["gc"] +
            count_score * weights["count"]
        )
        
        grade = score_to_grade(final_score)
        
        # Generate recommendations
        if dimer_score < 70:
            worst = matrix.worst_dimer
            if worst:
                recommendations.append(
                    f"Consider removing or redesigning primer pair containing "
                    f"{worst.primer1_name.split('_')[0]}"
                )
        
        if tm_score < 70:
            recommendations.append(
                "Redesign primers to achieve more uniform Tm values"
            )
        
        if gc_score < 70:
            recommendations.append(
                "Redesign primers to achieve more uniform GC content"
            )
        
        if len(pairs) > 5 and count_score < 80:
            recommendations.append(
                "Consider splitting into smaller multiplex groups"
            )
        
        # Build config used for reproducibility
        config_used = {
            "mode": self.mode,
            "settings": self.settings,
            "component_scores": {
                "dimer": dimer_score,
                "tm": tm_score,
                "gc": gc_score,
                "count": count_score,
            },
        }
        
        return MultiplexResult(
            pairs=pairs,
            matrix=matrix,
            score=round(final_score, 1),
            grade=grade,
            warnings=all_warnings,
            recommendations=recommendations,
            config_used=config_used,
        )
