"""
GC Profile Analysis for Amplicons.

Calculates GC content across sliding windows to assess uniformity.
"""

from typing import List
from .models import GCProfile


def calculate_gc_content(sequence: str) -> float:
    """Calculate GC percentage for a sequence."""
    if not sequence:
        return 0.0
    gc_count = sequence.upper().count("G") + sequence.upper().count("C")
    return (gc_count / len(sequence)) * 100


def calculate_gc_profile(
    sequence: str,
    window_size: int = 50,
    step_size: int = 10,
    ideal_min: float = 40.0,
    ideal_max: float = 60.0
) -> GCProfile:
    """
    Calculate GC content profile across amplicon.
    
    Args:
        sequence: DNA sequence
        window_size: Size of sliding window (bp)
        step_size: Step size between windows
        ideal_min: Minimum ideal GC %
        ideal_max: Maximum ideal GC %
        
    Returns:
        GCProfile with positions, values, and uniformity score
    """
    seq = sequence.upper()
    positions = []
    gc_values = []
    
    # Sliding window
    for i in range(0, len(seq) - window_size + 1, step_size):
        window = seq[i:i + window_size]
        gc = calculate_gc_content(window)
        positions.append(i + window_size // 2)  # Center of window
        gc_values.append(gc)
    
    if not gc_values:
        # Sequence too short for window
        gc = calculate_gc_content(seq)
        return GCProfile(
            positions=[len(seq) // 2],
            gc_values=[gc],
            window_size=len(seq),
            step_size=step_size,
            uniformity_score=100.0,
            min_gc=gc,
            max_gc=gc,
            avg_gc=gc
        )
    
    min_gc = min(gc_values)
    max_gc = max(gc_values)
    avg_gc = sum(gc_values) / len(gc_values)
    
    # Calculate uniformity score
    # Penalize for spread and deviation from ideal range
    spread = max_gc - min_gc
    spread_penalty = min(spread * 2, 50)  # Max 50 points penalty
    
    # Penalty for values outside ideal range
    outside_penalty = 0
    for gc in gc_values:
        if gc < ideal_min:
            outside_penalty += (ideal_min - gc) * 0.5
        elif gc > ideal_max:
            outside_penalty += (gc - ideal_max) * 0.5
    outside_penalty = min(outside_penalty, 50)  # Max 50 points
    
    uniformity_score = max(0, 100 - spread_penalty - outside_penalty)
    
    return GCProfile(
        positions=positions,
        gc_values=gc_values,
        window_size=window_size,
        step_size=step_size,
        uniformity_score=uniformity_score,
        min_gc=min_gc,
        max_gc=max_gc,
        avg_gc=avg_gc
    )


def generate_ascii_plot(profile: GCProfile, width: int = 60, height: int = 10) -> str:
    """Generate ASCII plot of GC profile for reports."""
    if not profile.gc_values:
        return "No data"
    
    lines = []
    lines.append(f"GC Profile (window={profile.window_size}bp)")
    lines.append("=" * width)
    
    min_val = max(0, profile.min_gc - 10)
    max_val = min(100, profile.max_gc + 10)
    range_val = max_val - min_val
    
    # Create grid
    for row in range(height, -1, -1):
        threshold = min_val + (row / height) * range_val
        line = f"{threshold:5.1f}% |"
        
        for gc in profile.gc_values:
            if gc >= threshold:
                line += "█"
            else:
                line += " "
        
        lines.append(line)
    
    # X-axis
    lines.append("       +" + "-" * len(profile.gc_values))
    lines.append(f"        Position (0-{profile.positions[-1] if profile.positions else 0}bp)")
    lines.append(f"        Avg: {profile.avg_gc:.1f}% | Range: {profile.min_gc:.1f}-{profile.max_gc:.1f}%")
    
    return "\n".join(lines)
