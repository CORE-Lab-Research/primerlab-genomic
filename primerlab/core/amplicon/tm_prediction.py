"""
Amplicon Tm Prediction.

Uses nearest-neighbor thermodynamics to predict melting temperature.
"""

import logging
from .models import AmpliconTm

logger = logging.getLogger(__name__)

# Nearest-neighbor parameters (SantaLucia 1998, DNA)
# ΔH in kcal/mol, ΔS in cal/(mol·K)
NN_PARAMS = {
    "AA": (-7.9, -22.2),
    "TT": (-7.9, -22.2),
    "AT": (-7.2, -20.4),
    "TA": (-7.2, -21.3),
    "CA": (-8.5, -22.7),
    "TG": (-8.5, -22.7),
    "GT": (-8.4, -22.4),
    "AC": (-8.4, -22.4),
    "CT": (-7.8, -21.0),
    "AG": (-7.8, -21.0),
    "GA": (-8.2, -22.2),
    "TC": (-8.2, -22.2),
    "CG": (-10.6, -27.2),
    "GC": (-9.8, -24.4),
    "GG": (-8.0, -19.9),
    "CC": (-8.0, -19.9),
}

# Initiation parameters
INIT_GC = (0.1, -2.8)  # ΔH, ΔS for terminal G or C
INIT_AT = (2.3, 4.1)   # ΔH, ΔS for terminal A or T


def predict_amplicon_tm(
    sequence: str,
    na_concentration: float = 50.0,  # mM
    mg_concentration: float = 0.0,   # mM
    dntp_concentration: float = 0.0  # mM
) -> AmpliconTm:
    """
    Predict amplicon melting temperature using nearest-neighbor method.
    
    Args:
        sequence: DNA sequence
        na_concentration: Na+ concentration in mM
        mg_concentration: Mg2+ concentration in mM (not yet implemented)
        dntp_concentration: dNTP concentration in mM (not yet implemented)
        
    Returns:
        AmpliconTm with predicted Tm
    """
    seq = sequence.upper()
    
    if len(seq) < 2:
        return AmpliconTm(tm=0.0, na_concentration=na_concentration)
    
    # Calculate ΔH and ΔS
    delta_h = 0.0  # kcal/mol
    delta_s = 0.0  # cal/(mol·K)
    
    # Initiation
    if seq[0] in "GC":
        delta_h += INIT_GC[0]
        delta_s += INIT_GC[1]
    else:
        delta_h += INIT_AT[0]
        delta_s += INIT_AT[1]
    
    if seq[-1] in "GC":
        delta_h += INIT_GC[0]
        delta_s += INIT_GC[1]
    else:
        delta_h += INIT_AT[0]
        delta_s += INIT_AT[1]
    
    # Nearest-neighbor contributions
    for i in range(len(seq) - 1):
        dinuc = seq[i:i+2]
        if dinuc in NN_PARAMS:
            dh, ds = NN_PARAMS[dinuc]
            delta_h += dh
            delta_s += ds
        else:
            # Unknown base, use average
            delta_h += -8.0
            delta_s += -22.0
    
    # Salt correction (SantaLucia 1998)
    # ΔS_corrected = ΔS + 0.368 * N * ln([Na+])
    # where N is length and [Na+] is in M
    na_molar = na_concentration / 1000.0
    if na_molar > 0:
        import math
        delta_s += 0.368 * len(seq) * math.log(na_molar)
    
    # Calculate Tm
    # Tm = ΔH / (ΔS + R * ln(Ct/4)) - 273.15
    # For amplicons (double-stranded), use simplified:
    # Tm = ΔH * 1000 / (ΔS + 1.987 * ln(1e-9)) - 273.15
    R = 1.987  # Gas constant cal/(mol·K)
    Ct = 1e-9  # Assume 1 nM total strand concentration
    
    import math
    denominator = delta_s + R * math.log(Ct / 4)
    
    if denominator >= 0:
        # Entropy too positive, use empirical formula
        tm = 81.5 + 0.41 * (sum(1 for b in seq if b in "GC") / len(seq) * 100) - 675 / len(seq)
    else:
        tm = (delta_h * 1000) / denominator - 273.15
    
    # Estimate melting curve width (sharpness)
    # Longer sequences have sharper melting curves
    width = max(1.0, 20.0 - len(seq) * 0.02)
    
    return AmpliconTm(
        tm=round(tm, 1),
        method="nearest-neighbor",
        na_concentration=na_concentration,
        width=round(width, 1)
    )
