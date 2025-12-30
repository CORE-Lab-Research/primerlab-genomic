"""
qPCR Module.

Provides qPCR-specific functionality including probe binding simulation,
amplicon validation, melt curve prediction, and efficiency estimation.
"""

from .probe_binding import (
    calculate_probe_binding_tm,
    simulate_probe_binding,
    ProbeBindingResult,
)
from .probe_position import (
    analyze_probe_position,
    optimize_probe_position,
)
from .amplicon_qc import (
    validate_qpcr_amplicon,
    score_qpcr_efficiency,
    QpcrAmpliconQC,
)
from .melt_curve import (
    predict_melt_curve,
    MeltCurveResult,
    MeltPeak,
)
from .melt_report import (
    generate_melt_markdown,
    generate_melt_csv,
    generate_melt_json,
)

__all__ = [
    # Probe binding
    "calculate_probe_binding_tm",
    "simulate_probe_binding",
    "ProbeBindingResult",
    # Probe position
    "analyze_probe_position",
    "optimize_probe_position",
    # Amplicon QC
    "validate_qpcr_amplicon",
    "score_qpcr_efficiency",
    "QpcrAmpliconQC",
    # Melt curve
    "predict_melt_curve",
    "MeltCurveResult",
    "MeltPeak",
    "generate_melt_markdown",
    "generate_melt_csv",
    "generate_melt_json",
]
