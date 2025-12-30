"""
PrimerLab Public API.

Provides high-level functions for external applications.
"""

from .public import (
    # Core functions
    design_pcr_primers,
    design_qpcr_assays,
    validate_primers,
    check_offtargets,
    
    # v0.4.x functions
    check_primer_compatibility,
    analyze_amplicon,
    run_overlap_simulation,
    check_species_specificity_api,
    
    # v0.4.3 functions
    simulate_tm_gradient_api,
    batch_species_check_api,
    
    # v0.5.0 functions
    simulate_probe_binding_api,
)

__all__ = [
    "design_pcr_primers",
    "design_qpcr_assays",
    "validate_primers",
    "check_offtargets",
    "check_primer_compatibility",
    "analyze_amplicon",
    "run_overlap_simulation",
    "check_species_specificity_api",
    "simulate_tm_gradient_api",
    "batch_species_check_api",
    "simulate_probe_binding_api",
]
