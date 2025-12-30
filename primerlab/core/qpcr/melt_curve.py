"""
SYBR Green Melt Curve Prediction Engine.

Predicts melt curve characteristics for SYBR Green qPCR amplicons.
Identifies potential multiple peaks that may indicate non-specific products.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


@dataclass
class MeltPeak:
    """Represents a peak in the melt curve."""
    temperature: float
    height: float  # Relative peak height (0-1)
    width: float   # Peak width at half maximum
    is_primary: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "temperature": round(self.temperature, 1),
            "height": round(self.height, 3),
            "width": round(self.width, 2),
            "is_primary": self.is_primary,
        }


@dataclass
class MeltCurveResult:
    """Result of melt curve prediction."""
    amplicon_sequence: str
    predicted_tm: float
    tm_range: Tuple[float, float]  # Expected Tm range
    peaks: List[MeltPeak]
    melt_curve: List[Dict[str, float]]  # Temperature vs -dF/dT
    is_single_peak: bool
    quality_score: float
    grade: str
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "amplicon_sequence": self.amplicon_sequence[:50] + "..." if len(self.amplicon_sequence) > 50 else self.amplicon_sequence,
            "amplicon_length": len(self.amplicon_sequence),
            "predicted_tm": round(self.predicted_tm, 1),
            "tm_range": (round(self.tm_range[0], 1), round(self.tm_range[1], 1)),
            "peaks": [p.to_dict() for p in self.peaks],
            "melt_curve": self.melt_curve,
            "is_single_peak": self.is_single_peak,
            "quality_score": round(self.quality_score, 1),
            "grade": self.grade,
            "warnings": self.warnings,
        }


def calculate_amplicon_tm(
    sequence: str,
    na_concentration: float = 50.0,
) -> float:
    """
    Calculate amplicon melting temperature.
    
    Uses the empirical formula for longer DNA:
    Tm = 81.5 + 16.6*log10([Na+]) + 0.41*(%GC) - 675/length
    
    Args:
        sequence: Amplicon sequence
        na_concentration: Na+ concentration in mM
        
    Returns:
        Predicted Tm in °C
    """
    if len(sequence) == 0:
        return 0.0
    
    seq = sequence.upper()
    gc_count = seq.count('G') + seq.count('C')
    gc_percent = (gc_count / len(seq)) * 100
    length = len(seq)
    
    # Convert mM to M for log
    na_m = na_concentration / 1000.0
    
    tm = 81.5 + 16.6 * math.log10(na_m) + 0.41 * gc_percent - 675 / length
    
    return tm


def generate_melt_curve(
    tm: float,
    width: float = 2.0,
    min_temp: float = 65.0,
    max_temp: float = 95.0,
    step: float = 0.2,
) -> List[Dict[str, float]]:
    """
    Generate theoretical melt curve data points.
    
    Models the derivative of fluorescence (-dF/dT) as a Gaussian peak.
    
    Args:
        tm: Melting temperature
        width: Peak width (standard deviation)
        min_temp: Starting temperature
        max_temp: Ending temperature
        step: Temperature step
        
    Returns:
        List of {temperature, derivative} data points
    """
    curve = []
    temp = min_temp
    
    while temp <= max_temp:
        # Gaussian curve for -dF/dT
        derivative = math.exp(-0.5 * ((temp - tm) / width) ** 2)
        
        curve.append({
            "temperature": round(temp, 1),
            "derivative": round(derivative, 4),
        })
        
        temp += step
    
    return curve


def detect_secondary_peaks(
    sequence: str,
    primary_tm: float,
) -> List[MeltPeak]:
    """
    Detect potential secondary peaks from sequence analysis.
    
    Looks for:
    - Primer-dimers (short products)
    - Non-specific products (regions with different GC)
    
    Args:
        sequence: Amplicon sequence
        primary_tm: Primary peak Tm
        
    Returns:
        List of detected peaks
    """
    peaks = [MeltPeak(
        temperature=primary_tm,
        height=1.0,
        width=2.0,
        is_primary=True,
    )]
    
    # Check for potential secondary products
    seq = sequence.upper()
    length = len(seq)
    
    if length < 20:
        return peaks
    
    # Analyze sequence regions for GC variation
    window_size = min(30, length // 3)
    gc_values = []
    
    for i in range(0, length - window_size, window_size):
        window = seq[i:i + window_size]
        gc = (window.count('G') + window.count('C')) / len(window) * 100
        gc_values.append(gc)
    
    # Check for significant GC variation (potential secondary structure)
    if len(gc_values) >= 2:
        gc_variation = max(gc_values) - min(gc_values)
        
        if gc_variation > 20:  # Significant variation
            # May produce secondary peak
            secondary_tm = primary_tm - (gc_variation * 0.3)
            peaks.append(MeltPeak(
                temperature=secondary_tm,
                height=0.2,  # Smaller peak
                width=3.0,   # Broader
                is_primary=False,
            ))
    
    # Check for self-complementary regions (potential primer-dimer artifact)
    # Simple check: look for inverted repeats
    half = length // 2
    for i in range(min(10, half)):
        forward = seq[i:i+6]
        reverse_region = seq[-(i+6):-(i) if i > 0 else None]
        if reverse_region:
            # Check for complementarity
            comp = {"A": "T", "T": "A", "G": "C", "C": "G"}
            rev_comp = "".join(comp.get(b, "N") for b in reversed(forward))
            if rev_comp in reverse_region:
                # Potential self-annealing
                dimer_tm = primary_tm - 15  # Lower Tm for dimer
                peaks.append(MeltPeak(
                    temperature=dimer_tm,
                    height=0.1,
                    width=2.5,
                    is_primary=False,
                ))
                break
    
    return peaks


def predict_melt_curve(
    amplicon_sequence: str,
    na_concentration: float = 50.0,
    min_temp: float = 65.0,
    max_temp: float = 95.0,
    step: float = 0.2,
) -> MeltCurveResult:
    """
    Predict SYBR Green melt curve for an amplicon.
    
    Args:
        amplicon_sequence: Amplicon DNA sequence
        na_concentration: Na+ concentration in mM
        min_temp: Minimum temperature for curve
        max_temp: Maximum temperature for curve
        step: Temperature step
        
    Returns:
        MeltCurveResult with predicted curve and analysis
    """
    warnings = []
    
    # Calculate primary Tm
    primary_tm = calculate_amplicon_tm(amplicon_sequence, na_concentration)
    
    # Tm range (typical variation ±2°C)
    tm_range = (primary_tm - 2.0, primary_tm + 2.0)
    
    # Detect peaks (primary and potential secondary)
    peaks = detect_secondary_peaks(amplicon_sequence, primary_tm)
    
    # Generate composite melt curve
    curve = generate_melt_curve(primary_tm, min_temp=min_temp, max_temp=max_temp, step=step)
    
    # Add secondary peaks to curve if present
    for peak in peaks[1:]:  # Skip primary
        secondary_curve = generate_melt_curve(
            peak.temperature, 
            width=peak.width,
            min_temp=min_temp, 
            max_temp=max_temp, 
            step=step
        )
        # Combine curves
        for i, point in enumerate(curve):
            if i < len(secondary_curve):
                point["derivative"] += secondary_curve[i]["derivative"] * peak.height
    
    # Normalize curve
    max_deriv = max(p["derivative"] for p in curve)
    if max_deriv > 0:
        for point in curve:
            point["derivative"] = round(point["derivative"] / max_deriv, 4)
    
    # Evaluate quality
    is_single_peak = len(peaks) == 1
    
    score = 100.0
    
    # Amplicon length check
    amp_len = len(amplicon_sequence)
    if amp_len < 70:
        warnings.append(f"Amplicon too short ({amp_len} bp). May be difficult to distinguish from primer-dimers.")
        score -= 15
    elif amp_len > 200:
        warnings.append(f"Amplicon long ({amp_len} bp). Broader melt peak expected.")
        score -= 5
    
    # GC content check
    gc = (amplicon_sequence.upper().count('G') + amplicon_sequence.upper().count('C')) / amp_len * 100
    if gc < 30 or gc > 70:
        warnings.append(f"Extreme GC content ({gc:.1f}%). Tm prediction may be less accurate.")
        score -= 10
    
    # Multiple peaks
    if not is_single_peak:
        warnings.append(f"Multiple peaks predicted ({len(peaks)}). May indicate non-specific products.")
        score -= 20
    
    # Tm check
    if primary_tm < 75:
        warnings.append(f"Low Tm ({primary_tm:.1f}°C). Increase amplicon length or GC content.")
        score -= 10
    elif primary_tm > 90:
        warnings.append(f"High Tm ({primary_tm:.1f}°C). GC-rich amplicon may be difficult to melt.")
        score -= 5
    
    score = max(0.0, min(100.0, score))
    
    # Grade
    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"
    
    return MeltCurveResult(
        amplicon_sequence=amplicon_sequence,
        predicted_tm=primary_tm,
        tm_range=tm_range,
        peaks=peaks,
        melt_curve=curve,
        is_single_peak=is_single_peak,
        quality_score=score,
        grade=grade,
        warnings=warnings,
    )
