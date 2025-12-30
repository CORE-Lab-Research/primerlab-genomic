"""
Probe Binding Engine for TaqMan qPCR.

Simulates probe-template binding using nearest-neighbor thermodynamics.
Calculates binding efficiency across temperature gradients.

Based on SantaLucia (1998) and Allawi & SantaLucia (1997) parameters.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# Nearest-neighbor ΔH and ΔS values (kcal/mol and cal/mol·K)
# SantaLucia (1998) unified parameters
NN_PARAMS = {
    "AA": {"dH": -7.9, "dS": -22.2},
    "TT": {"dH": -7.9, "dS": -22.2},
    "AT": {"dH": -7.2, "dS": -20.4},
    "TA": {"dH": -7.2, "dS": -21.3},
    "CA": {"dH": -8.5, "dS": -22.7},
    "TG": {"dH": -8.5, "dS": -22.7},
    "GT": {"dH": -8.4, "dS": -22.4},
    "AC": {"dH": -8.4, "dS": -22.4},
    "CT": {"dH": -7.8, "dS": -21.0},
    "AG": {"dH": -7.8, "dS": -21.0},
    "GA": {"dH": -8.2, "dS": -22.2},
    "TC": {"dH": -8.2, "dS": -22.2},
    "CG": {"dH": -10.6, "dS": -27.2},
    "GC": {"dH": -9.8, "dS": -24.4},
    "GG": {"dH": -8.0, "dS": -19.9},
    "CC": {"dH": -8.0, "dS": -19.9},
}

# Initiation parameters
INIT_PARAMS = {
    "AT_terminal": {"dH": 2.3, "dS": 4.1},
    "GC_terminal": {"dH": 0.1, "dS": -2.8},
}


@dataclass
class ProbeBindingResult:
    """Result of probe binding simulation."""
    probe_sequence: str
    probe_tm: float
    binding_efficiency: float
    optimal_temp: float
    binding_curve: List[Dict[str, float]] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    grade: str = "A"
    score: float = 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "probe_sequence": self.probe_sequence,
            "probe_tm": round(self.probe_tm, 2),
            "binding_efficiency": round(self.binding_efficiency, 2),
            "optimal_temp": round(self.optimal_temp, 2),
            "binding_curve": self.binding_curve,
            "warnings": self.warnings,
            "grade": self.grade,
            "score": round(self.score, 1),
        }


def calculate_nearest_neighbor_tm(
    sequence: str,
    na_concentration: float = 50.0,  # mM
    probe_concentration: float = 0.25,  # μM
) -> tuple:
    """
    Calculate Tm using nearest-neighbor method.
    
    Args:
        sequence: DNA sequence (5' to 3')
        na_concentration: Na+ concentration in mM
        probe_concentration: Probe concentration in μM
        
    Returns:
        Tuple of (Tm, total_dH, total_dS)
    """
    if len(sequence) < 2:
        return (0.0, 0.0, 0.0)
    
    seq = sequence.upper()
    total_dH = 0.0  # kcal/mol
    total_dS = 0.0  # cal/mol·K
    
    # Sum nearest-neighbor contributions
    for i in range(len(seq) - 1):
        dinucleotide = seq[i:i+2]
        if dinucleotide in NN_PARAMS:
            total_dH += NN_PARAMS[dinucleotide]["dH"]
            total_dS += NN_PARAMS[dinucleotide]["dS"]
        else:
            # Handle unknown bases (N, etc.)
            total_dH += -7.5  # Average
            total_dS += -21.0
    
    # Terminal corrections
    first_base = seq[0]
    last_base = seq[-1]
    
    if first_base in "AT":
        total_dH += INIT_PARAMS["AT_terminal"]["dH"]
        total_dS += INIT_PARAMS["AT_terminal"]["dS"]
    else:
        total_dH += INIT_PARAMS["GC_terminal"]["dH"]
        total_dS += INIT_PARAMS["GC_terminal"]["dS"]
    
    if last_base in "AT":
        total_dH += INIT_PARAMS["AT_terminal"]["dH"]
        total_dS += INIT_PARAMS["AT_terminal"]["dS"]
    else:
        total_dH += INIT_PARAMS["GC_terminal"]["dH"]
        total_dS += INIT_PARAMS["GC_terminal"]["dS"]
    
    # Convert concentrations
    na_mol = na_concentration / 1000.0  # M
    probe_mol = probe_concentration / 1000000.0  # M
    
    # Salt correction (SantaLucia 1998)
    # ΔS = ΔS + 0.368 * N * ln([Na+])
    n_bp = len(seq) - 1
    salt_correction = 0.368 * n_bp * math.log(na_mol)
    total_dS_corrected = total_dS + salt_correction
    
    # Calculate Tm
    # Tm = (ΔH * 1000) / (ΔS + R * ln(Ct/4)) - 273.15
    R = 1.987  # cal/mol·K
    if probe_mol > 0:
        tm = (total_dH * 1000) / (total_dS_corrected + R * math.log(probe_mol / 4)) - 273.15
    else:
        tm = (total_dH * 1000) / total_dS_corrected - 273.15
    
    return (tm, total_dH, total_dS)


def calculate_probe_binding_tm(
    probe_sequence: str,
    na_concentration: float = 50.0,
    probe_concentration: float = 0.25,
) -> float:
    """
    Calculate probe binding Tm.
    
    Args:
        probe_sequence: Probe sequence (5' to 3')
        na_concentration: Na+ concentration in mM
        probe_concentration: Probe concentration in μM
        
    Returns:
        Calculated Tm in °C
    """
    tm, _, _ = calculate_nearest_neighbor_tm(
        probe_sequence, na_concentration, probe_concentration
    )
    return tm


def calculate_binding_efficiency(
    tm: float,
    annealing_temp: float,
) -> float:
    """
    Calculate binding efficiency at a given annealing temperature.
    
    Uses a sigmoid model where efficiency drops as temperature
    approaches and exceeds Tm.
    
    Args:
        tm: Probe Tm in °C
        annealing_temp: Annealing temperature in °C
        
    Returns:
        Binding efficiency (0-100%)
    """
    # Probe should have Tm ~8-10°C higher than annealing temp
    # Efficiency drops as temp approaches Tm
    
    delta = tm - annealing_temp
    
    if delta > 15:
        # Too far below Tm - stable but check for non-specific
        return 100.0
    elif delta > 10:
        # Optimal range (8-10°C below Tm)
        return 99.0
    elif delta > 5:
        # Acceptable
        return 95.0
    elif delta > 0:
        # Getting close to Tm
        return 80.0 - (5 - delta) * 10
    else:
        # Above Tm - probe will dissociate
        return max(0.0, 30.0 + delta * 5)


def simulate_probe_binding(
    probe_sequence: str,
    target_sequence: Optional[str] = None,
    min_temp: float = 55.0,
    max_temp: float = 72.0,
    step_size: float = 0.5,
    na_concentration: float = 50.0,
    probe_concentration: float = 0.25,
) -> ProbeBindingResult:
    """
    Simulate probe binding across temperature range.
    
    Args:
        probe_sequence: Probe sequence
        target_sequence: Optional template for mismatch detection
        min_temp: Minimum temperature
        max_temp: Maximum temperature
        step_size: Temperature step
        na_concentration: Na+ concentration (mM)
        probe_concentration: Probe concentration (μM)
        
    Returns:
        ProbeBindingResult with binding curve
    """
    warnings = []
    
    # Calculate probe Tm
    probe_tm = calculate_probe_binding_tm(
        probe_sequence, na_concentration, probe_concentration
    )
    
    # Check probe length
    if len(probe_sequence) < 18:
        warnings.append(f"Probe too short ({len(probe_sequence)} bp). Minimum 18 bp recommended.")
    if len(probe_sequence) > 30:
        warnings.append(f"Probe too long ({len(probe_sequence)} bp). Maximum 30 bp recommended.")
    
    # Check GC content
    gc_count = probe_sequence.upper().count('G') + probe_sequence.upper().count('C')
    gc_percent = (gc_count / len(probe_sequence)) * 100
    if gc_percent < 30:
        warnings.append(f"Probe GC content too low ({gc_percent:.1f}%). Minimum 30% recommended.")
    if gc_percent > 80:
        warnings.append(f"Probe GC content too high ({gc_percent:.1f}%). Maximum 80% recommended.")
    
    # Check 5' G rule (G at 5' end can quench fluorescence)
    if probe_sequence.upper().startswith('G'):
        warnings.append("Probe has G at 5' end - may quench fluorescence. Consider redesign.")
    
    # Generate binding curve
    binding_curve = []
    best_efficiency = 0.0
    optimal_temp = min_temp
    
    temp = min_temp
    while temp <= max_temp:
        efficiency = calculate_binding_efficiency(probe_tm, temp)
        binding_curve.append({
            "temperature": round(temp, 1),
            "efficiency": round(efficiency, 2),
        })
        
        if efficiency > best_efficiency:
            best_efficiency = efficiency
            optimal_temp = temp
        
        temp += step_size
    
    # Calculate grade
    score = best_efficiency
    if warnings:
        score -= len(warnings) * 5
    
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
    
    return ProbeBindingResult(
        probe_sequence=probe_sequence,
        probe_tm=probe_tm,
        binding_efficiency=best_efficiency,
        optimal_temp=optimal_temp,
        binding_curve=binding_curve,
        warnings=warnings,
        grade=grade,
        score=score,
    )
