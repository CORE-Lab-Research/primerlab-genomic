"""
Batch Input Loader for Species-Check.

Load multiple primer files and multi-FASTA templates.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class BatchInput:
    """Container for batch species-check input."""
    primer_files: List[Path] = field(default_factory=list)
    primer_data: Dict[str, List[Dict]] = field(default_factory=dict)  # filename -> primers
    template_files: List[Path] = field(default_factory=list)
    total_primers: int = 0
    total_templates: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primer_files": [str(p) for p in self.primer_files],
            "template_files": [str(t) for t in self.template_files],
            "total_primers": self.total_primers,
            "total_templates": self.total_templates
        }


def load_primers_from_directory(
    directory: str,
    pattern: str = "*.json"
) -> BatchInput:
    """
    Load all primer JSON files from a directory.
    
    Args:
        directory: Path to directory containing primer JSONs
        pattern: Glob pattern for file matching
        
    Returns:
        BatchInput with all loaded primers
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    batch = BatchInput()
    
    for file_path in sorted(dir_path.glob(pattern)):
        try:
            with open(file_path, "r") as f:
                primers = json.load(f)
            
            if isinstance(primers, list):
                # Normalize primer format
                normalized = []
                for i, p in enumerate(primers):
                    normalized.append({
                        "name": p.get("name", f"Primer_{i+1}"),
                        "forward": p.get("forward", p.get("fwd", "")),
                        "reverse": p.get("reverse", p.get("rev", ""))
                    })
                
                batch.primer_files.append(file_path)
                batch.primer_data[file_path.name] = normalized
                batch.total_primers += len(normalized)
                
                logger.info(f"Loaded {len(normalized)} primers from {file_path.name}")
        
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
    
    return batch


def load_multi_fasta_templates(fasta_path: str) -> Dict[str, str]:
    """
    Load multiple templates from a single multi-FASTA file.
    
    Args:
        fasta_path: Path to multi-FASTA file
        
    Returns:
        Dict mapping species_name -> sequence
    """
    path = Path(fasta_path)
    if not path.exists():
        raise FileNotFoundError(f"FASTA file not found: {fasta_path}")
    
    templates = {}
    current_name = None
    current_seq = []
    
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith(">"):
                # Save previous sequence
                if current_name and current_seq:
                    templates[current_name] = "".join(current_seq).upper()
                
                # Start new sequence
                header = line[1:].split()[0]  # Take first word after >
                current_name = header
                current_seq = []
            else:
                current_seq.append(line)
    
    # Save last sequence
    if current_name and current_seq:
        templates[current_name] = "".join(current_seq).upper()
    
    logger.info(f"Loaded {len(templates)} templates from {path.name}")
    return templates


def load_primer_files(file_paths: List[str]) -> BatchInput:
    """
    Load primers from specific file paths.
    
    Args:
        file_paths: List of paths to primer JSON files
        
    Returns:
        BatchInput with all loaded primers
    """
    batch = BatchInput()
    
    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"File not found: {file_path}")
            continue
        
        try:
            with open(path, "r") as f:
                primers = json.load(f)
            
            if isinstance(primers, list):
                normalized = []
                for i, p in enumerate(primers):
                    normalized.append({
                        "name": p.get("name", f"Primer_{i+1}"),
                        "forward": p.get("forward", p.get("fwd", "")),
                        "reverse": p.get("reverse", p.get("rev", ""))
                    })
                
                batch.primer_files.append(path)
                batch.primer_data[path.name] = normalized
                batch.total_primers += len(normalized)
        
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
    
    return batch
