"""
Audit Log Generator (v0.1.4)

Logs all parameters and results for reproducibility.
Creates audit.json in output directory.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional

from primerlab import __version__
from primerlab.core.logger import get_logger

logger = get_logger()


def generate_hash(data: str, length: int = 12) -> str:
    """Generate SHA256 hash of data."""
    full_hash = hashlib.sha256(data.encode()).hexdigest()
    return f"sha256:{full_hash[:length]}"


def create_audit_log(
    workflow: str,
    config: Dict[str, Any],
    sequence: Optional[str],
    results: Dict[str, Any],
    output_dir: Path
) -> Path:
    """
    Create audit log file.
    
    Args:
        workflow: Workflow type (pcr/qpcr)
        config: Full configuration dict
        sequence: Input sequence (will be hashed)
        results: Workflow results
        output_dir: Directory to save audit.json
    
    Returns:
        Path to audit.json file
    """
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    
    # Hash sensitive data
    config_str = json.dumps(config, sort_keys=True)
    config_hash = generate_hash(config_str)
    
    sequence_hash = generate_hash(sequence) if sequence else None
    sequence_length = len(sequence) if sequence else 0
    
    # Extract key parameters
    params = config.get("parameters", {})
    qc_config = config.get("qc", {})
    
    # Build audit entry
    audit_entry = {
        "primerlab_version": __version__,
        "timestamp": timestamp,
        "workflow": workflow,
        "qc_mode": qc_config.get("mode", "standard"),
        "config_hash": config_hash,
        "input": {
            "sequence_length": sequence_length,
            "sequence_hash": sequence_hash,
        },
        "parameters_summary": {
            "tm_range": _format_range(params.get("tm", {})),
            "product_size": params.get("product_size_range", "N/A"),
            "gc_range": _format_range(params.get("gc", {})),
            "primer_size": _format_range(params.get("primer_size", {})),
        },
        "results": {
            "success": results.get("success", False),
            "quality_score": results.get("quality_score"),
            "quality_category": results.get("quality_category"),
            "candidates_evaluated": results.get("candidates_evaluated", 0),
            "candidates_passed_qc": results.get("candidates_passed_qc", 0),
            "primers_designed": results.get("primers_designed", 0),
            "alternatives_count": results.get("alternatives_count", 0),
        },
        "qc_thresholds": {
            "hairpin_dg_max": qc_config.get("hairpin_dg_max"),
            "homodimer_dg_max": qc_config.get("homodimer_dg_max"),
            "heterodimer_dg_max": qc_config.get("heterodimer_dg_max"),
            "tm_diff_max": qc_config.get("tm_diff_max"),
        }
    }
    
    # Save to file
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audit_path = output_dir / "audit.json"
    
    with open(audit_path, "w") as f:
        json.dump(audit_entry, f, indent=2)
    
    logger.info(f"Audit log saved: {audit_path}")
    
    return audit_path


def _format_range(param_dict: Dict[str, Any]) -> str:
    """Format min/max or min/opt/max range as string."""
    if not param_dict:
        return "N/A"
    
    min_val = param_dict.get("min")
    max_val = param_dict.get("max")
    
    if min_val is not None and max_val is not None:
        return f"{min_val}-{max_val}"
    
    return "N/A"


def append_audit_log(
    output_dir: Path,
    additional_data: Dict[str, Any]
) -> None:
    """
    Append additional data to existing audit log.
    
    Args:
        output_dir: Directory containing audit.json
        additional_data: Data to append
    """
    audit_path = Path(output_dir) / "audit.json"
    
    if not audit_path.exists():
        logger.warning("No audit.json found to append to")
        return
    
    with open(audit_path, "r") as f:
        audit_entry = json.load(f)
    
    audit_entry.update(additional_data)
    
    with open(audit_path, "w") as f:
        json.dump(audit_entry, f, indent=2)
    
    logger.debug(f"Audit log updated: {audit_path}")
