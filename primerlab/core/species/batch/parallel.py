"""
Parallel Species-Check Processing.

Multi-threaded batch processing for species specificity analysis.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..binding import check_species_specificity
from ..models import SpeciesTemplate, SpeciesCheckResult
from .batch_loader import BatchInput

logger = logging.getLogger(__name__)


@dataclass
class BatchSpeciesResult:
    """Result of batch species-check."""
    total_files: int = 0
    total_primers: int = 0
    processed: int = 0
    passed: int = 0
    failed: int = 0
    
    results: Dict[str, SpeciesCheckResult] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_files": self.total_files,
            "total_primers": self.total_primers,
            "processed": self.processed,
            "passed": self.passed,
            "failed": self.failed,
            "pass_rate": round(self.passed / max(1, self.processed) * 100, 1),
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "summary": self.summary
        }


def _process_single_file(
    filename: str,
    primers: List[Dict],
    target_template: SpeciesTemplate,
    offtarget_templates: Dict[str, SpeciesTemplate],
    config: Optional[Dict] = None
) -> tuple:
    """
    Process a single primer file.
    
    Returns:
        Tuple of (filename, SpeciesCheckResult)
    """
    try:
        result = check_species_specificity(
            primers,
            target_template,
            offtarget_templates,
            config
        )
        return (filename, result, None)
    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        return (filename, None, str(e))


def run_parallel_species_check(
    batch_input: BatchInput,
    target_template: SpeciesTemplate,
    offtarget_templates: Dict[str, SpeciesTemplate],
    config: Optional[Dict] = None,
    max_workers: int = 4,
    progress_callback: Optional[callable] = None
) -> BatchSpeciesResult:
    """
    Run species-check on multiple primer files in parallel.
    
    Args:
        batch_input: BatchInput with loaded primer data
        target_template: Target species template
        offtarget_templates: Dict of off-target templates
        config: Optional configuration
        max_workers: Maximum parallel threads
        progress_callback: Optional callback(processed, total)
        
    Returns:
        BatchSpeciesResult with all results
    """
    batch_result = BatchSpeciesResult(
        total_files=len(batch_input.primer_files),
        total_primers=batch_input.total_primers
    )
    
    if not batch_input.primer_data:
        logger.warning("No primer files to process")
        return batch_result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all jobs
        futures = {}
        for filename, primers in batch_input.primer_data.items():
            future = executor.submit(
                _process_single_file,
                filename,
                primers,
                target_template,
                offtarget_templates,
                config
            )
            futures[future] = filename
        
        # Collect results
        for future in as_completed(futures):
            filename = futures[future]
            
            try:
                fname, result, error = future.result()
                batch_result.processed += 1
                
                if result:
                    batch_result.results[fname] = result
                    if result.is_specific:
                        batch_result.passed += 1
                    else:
                        batch_result.failed += 1
                else:
                    batch_result.failed += 1
                
                if progress_callback:
                    progress_callback(batch_result.processed, batch_result.total_files)
                    
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
                batch_result.failed += 1
    
    # Generate summary
    if batch_result.results:
        scores = [r.overall_score for r in batch_result.results.values()]
        batch_result.summary = {
            "avg_score": round(sum(scores) / len(scores), 1),
            "min_score": min(scores),
            "max_score": max(scores),
            "pass_rate": round(batch_result.passed / max(1, batch_result.processed) * 100, 1)
        }
    
    return batch_result


def generate_batch_csv(
    batch_result: BatchSpeciesResult,
    output_path: str
) -> str:
    """
    Generate CSV summary of batch results.
    
    Args:
        batch_result: BatchSpeciesResult
        output_path: Path to output CSV
        
    Returns:
        Path to created CSV file
    """
    path = Path(output_path)
    
    lines = ["Filename,Score,Grade,Is_Specific,Primers_Checked,Warnings"]
    
    for filename, result in batch_result.results.items():
        warnings_str = "; ".join(result.warnings[:3]) if result.warnings else ""
        lines.append(
            f"{filename},{result.overall_score:.1f},{result.grade},"
            f"{result.is_specific},{result.primers_checked},\"{warnings_str}\""
        )
    
    # Add summary row
    lines.append("")
    lines.append(f"Total,{batch_result.summary.get('avg_score', 0):.1f},-,-,-,-")
    
    with open(path, "w") as f:
        f.write("\n".join(lines))
    
    logger.info(f"CSV report saved to {path}")
    return str(path)
