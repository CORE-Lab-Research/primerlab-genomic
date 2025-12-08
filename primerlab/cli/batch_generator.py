"""
Batch Config Generator - Generate multiple YAML configs from CSV input.

Usage:
    primerlab batch-generate --input sequences.csv --output configs/ --workflow pcr

CSV Format:
    name,sequence,tm_min,tm_max,product_min,product_max
    gene1,ATGC...,58,62,100,300
    gene2,ATGC...,58,62,100,300
"""

import csv
import os
from pathlib import Path
from typing import List, Dict, Any
import yaml

from primerlab.core.logger import get_logger

logger = get_logger()


def generate_configs_from_csv(
    csv_path: str,
    output_dir: str,
    workflow: str = "pcr",
    template: Dict[str, Any] = None,
    show_progress: bool = True
) -> List[str]:
    """
    Generates YAML config files from a CSV file.
    
    Args:
        csv_path: Path to input CSV file
        output_dir: Directory to save generated configs
        workflow: Workflow type (pcr, qpcr)
        template: Optional base template to use
        show_progress: Show progress bar (v0.1.3)
        
    Returns:
        List of paths to generated config files
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    generated_files = []
    
    # Default template
    base_template = template or {
        "workflow": workflow,
        "parameters": {
            "primer_size": {"min": 18, "opt": 20, "max": 24},
            "tm": {"min": 58.0, "opt": 60.0, "max": 62.0},
            "gc": {"min": 40.0, "max": 60.0}
        }
    }
    
    # Read CSV and count rows for progress bar
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    
    # Setup progress bar (v0.1.3)
    try:
        from tqdm import tqdm
        iterator = tqdm(rows, desc="Generating configs", disable=not show_progress)
    except ImportError:
        iterator = rows
        if show_progress:
            logger.info("Install tqdm for progress bar: pip install tqdm")
    
    for row in iterator:
        name = row.get('name', '').strip()
        sequence = row.get('sequence', '').strip()
        
        if not name or not sequence:
            logger.warning(f"Skipping row with missing name or sequence")
            continue
        
        # Create config from template
        config = {
            "workflow": workflow,
            "input": {
                "sequence": sequence
            },
            "parameters": dict(base_template.get("parameters", {})),
            "output": {
                "directory": f"output_{name}"
            }
        }
        
        # Override with CSV values if present
        if row.get('tm_min') and row.get('tm_max'):
            config["parameters"]["tm"] = {
                "min": float(row['tm_min']),
                "opt": float(row.get('tm_opt', (float(row['tm_min']) + float(row['tm_max'])) / 2)),
                "max": float(row['tm_max'])
            }
        
        if row.get('product_min') and row.get('product_max'):
            config["parameters"]["product_size"] = {
                "min": int(row['product_min']),
                "max": int(row['product_max'])
            }
        
        if row.get('gc_min') and row.get('gc_max'):
            config["parameters"]["gc"] = {
                "min": float(row['gc_min']),
                "max": float(row['gc_max'])
            }
        
        # Save config
        config_filename = f"{name}.yaml"
        config_path = output_path / config_filename
        
        with open(config_path, 'w') as cf:
            yaml.dump(config, cf, default_flow_style=False, sort_keys=False)
        
        generated_files.append(str(config_path))
    
    logger.info(f"Generated {len(generated_files)} config files in {output_dir}")
    return generated_files
