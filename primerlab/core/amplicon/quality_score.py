"""
Amplicon Quality Scoring.

Combines multiple metrics into overall quality assessment.
"""

from typing import List, Optional
from .models import (
    AmpliconQuality,
    SecondaryStructure,
    GCProfile,
    GCClamp,
    AmpliconTm
)


def score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 85:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 55:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def calculate_quality_score(
    sequence: str,
    structure: Optional[SecondaryStructure] = None,
    gc_profile: Optional[GCProfile] = None,
    gc_clamp: Optional[GCClamp] = None,
    amplicon_tm: Optional[AmpliconTm] = None,
    optimal_length_min: int = 100,
    optimal_length_max: int = 500,
    weights: dict = None
) -> AmpliconQuality:
    """
    Calculate overall amplicon quality score.
    
    Args:
        sequence: Amplicon sequence
        structure: Secondary structure prediction result
        gc_profile: GC profile analysis result  
        gc_clamp: GC clamp analysis result
        amplicon_tm: Tm prediction result
        optimal_length_min: Minimum optimal amplicon length
        optimal_length_max: Maximum optimal amplicon length
        weights: Custom weights for components
        
    Returns:
        AmpliconQuality with score, grade, and component breakdown
    """
    # Default weights
    if weights is None:
        weights = {
            "structure": 0.30,
            "gc_uniformity": 0.25,
            "gc_clamp": 0.20,
            "length": 0.15,
            "tm_sharpness": 0.10
        }
    
    warnings = []
    
    # 1. Structure score (0-100)
    structure_score = 100.0
    if structure:
        if structure.delta_g < -8.0:
            structure_score = 30.0
            warnings.append(f"Strong secondary structure (ΔG={structure.delta_g:.1f} kcal/mol)")
        elif structure.delta_g < -5.0:
            structure_score = 60.0
            warnings.append(f"Moderate secondary structure (ΔG={structure.delta_g:.1f} kcal/mol)")
        elif structure.delta_g < -3.0:
            structure_score = 80.0
        # else: 100 (weak or no structure)
    
    # 2. GC uniformity score (from profile)
    gc_uniformity_score = 100.0
    if gc_profile:
        gc_uniformity_score = gc_profile.uniformity_score
        if gc_profile.uniformity_score < 60:
            warnings.append(f"Non-uniform GC content (range: {gc_profile.min_gc:.1f}-{gc_profile.max_gc:.1f}%)")
    
    # 3. GC clamp score
    gc_clamp_score = 100.0
    if gc_clamp:
        gc_clamp_score = 100.0 if gc_clamp.is_optimal else 60.0
        if gc_clamp.warning:
            warnings.append(gc_clamp.warning)
    
    # 4. Length score
    length = len(sequence)
    length_score = 100.0
    if length < optimal_length_min:
        length_score = max(50, 100 - (optimal_length_min - length) * 2)
        warnings.append(f"Short amplicon ({length}bp < {optimal_length_min}bp)")
    elif length > optimal_length_max:
        length_score = max(50, 100 - (length - optimal_length_max) * 0.2)
        warnings.append(f"Long amplicon ({length}bp > {optimal_length_max}bp)")
    
    # 5. Tm sharpness score
    tm_sharpness_score = 100.0
    if amplicon_tm:
        # Lower width = sharper = better
        if amplicon_tm.width > 15:
            tm_sharpness_score = 60.0
            warnings.append("Broad melting curve expected")
        elif amplicon_tm.width > 10:
            tm_sharpness_score = 80.0
    
    # Calculate weighted score
    total_score = (
        structure_score * weights["structure"] +
        gc_uniformity_score * weights["gc_uniformity"] +
        gc_clamp_score * weights["gc_clamp"] +
        length_score * weights["length"] +
        tm_sharpness_score * weights["tm_sharpness"]
    )
    
    grade = score_to_grade(total_score)
    
    return AmpliconQuality(
        score=round(total_score, 1),
        grade=grade,
        structure_score=round(structure_score, 1),
        gc_uniformity_score=round(gc_uniformity_score, 1),
        gc_clamp_score=round(gc_clamp_score, 1),
        length_score=round(length_score, 1),
        tm_sharpness_score=round(tm_sharpness_score, 1),
        warnings=warnings
    )
