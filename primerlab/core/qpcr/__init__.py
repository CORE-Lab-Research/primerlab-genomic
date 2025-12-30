"""
qPCR Module.

Provides qPCR-specific functionality including probe binding simulation,
melt curve prediction, and efficiency estimation.
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

__all__ = [
    # Probe binding
    "calculate_probe_binding_tm",
    "simulate_probe_binding",
    "ProbeBindingResult",
    # Probe position
    "analyze_probe_position",
    "optimize_probe_position",
]
