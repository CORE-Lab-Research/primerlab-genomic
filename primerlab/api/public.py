"""
Public API for PrimerLab.
This module provides a high-level programmatic interface for external applications.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import WorkflowResult
from primerlab.workflows.pcr.workflow import run_pcr_workflow
from primerlab.workflows.qpcr.workflow import run_qpcr_workflow
from primerlab.core.config_loader import load_and_merge_config

def design_pcr_primers(sequence: str, config: Optional[Dict[str, Any]] = None) -> WorkflowResult:
    """
    Programmatic entry point for PCR primer design.
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
                If provided, it merges with/overrides default PCR settings.
        
    Returns:
        WorkflowResult object containing primers and QC status.
    """
    # Base config structure
    base_config = {
        "workflow": "pcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"} # Default output for API calls
    }
    
    # Merge with user config if provided
    # Note: In a full implementation, we might want to load pcr_default.yaml here first.
    # For now, we rely on the workflow to load defaults if not fully specified,
    # but passing a minimal config is safer.
    
    final_config = base_config
    if config:
        # Simple dictionary update for top-level keys (shallow merge for now)
        # For deep merge, we would use a utility.
        final_config.update(config)
        # Ensure input sequence is preserved if user accidentally overwrote it
        final_config["input"]["sequence"] = sequence

    return run_pcr_workflow(final_config)

def design_qpcr_assays(sequence: str, config: Optional[Dict[str, Any]] = None) -> WorkflowResult:
    """
    Programmatic entry point for qPCR assay design (primers + probe).
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
        
    Returns:
        WorkflowResult object containing primers, probe, and efficiency metrics.
    """
    base_config = {
        "workflow": "qpcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"}
    }
    
    final_config = base_config
    if config:
        final_config.update(config)
        final_config["input"]["sequence"] = sequence

    return run_qpcr_workflow(final_config)
