"""
Batch Comparison Analysis.

Compares multiple primer design runs and generates diff reports.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
import json
from primerlab.core.logger import get_logger

logger = get_logger()


@dataclass
class DesignRunSummary:
    """Summary of a single design run."""
    name: str
    path: str
    workflow: str
    success: bool
    quality_score: Optional[float] = None
    quality_grade: Optional[str] = None
    primer_count: int = 0
    forward_seq: str = ""
    reverse_seq: str = ""
    product_size: int = 0
    tm_forward: float = 0.0
    tm_reverse: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "workflow": self.workflow,
            "success": self.success,
            "quality_score": self.quality_score,
            "quality_grade": self.quality_grade,
            "forward": self.forward_seq[:20] + "..." if len(self.forward_seq) > 20 else self.forward_seq,
            "reverse": self.reverse_seq[:20] + "..." if len(self.reverse_seq) > 20 else self.reverse_seq,
            "product_size": self.product_size,
        }


@dataclass
class ComparisonResult:
    """Result of batch comparison."""
    runs: List[DesignRunSummary] = field(default_factory=list)
    differences: List[Dict[str, Any]] = field(default_factory=list)
    best_run: Optional[str] = None
    worst_run: Optional[str] = None
    avg_quality: float = 0.0
    success_rate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_count": len(self.runs),
            "runs": [r.to_dict() for r in self.runs],
            "differences": self.differences,
            "best_run": self.best_run,
            "worst_run": self.worst_run,
            "avg_quality": self.avg_quality,
            "success_rate": self.success_rate,
        }


class BatchComparator:
    """
    Compares multiple primer design runs.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize comparator."""
        self.config = config or {}
    
    def compare(self, result_paths: List[str]) -> ComparisonResult:
        """
        Compare multiple result files.
        
        Args:
            result_paths: List of paths to result.json files
            
        Returns:
            ComparisonResult with comparison data
        """
        logger.info(f"Comparing {len(result_paths)} design runs")
        
        runs = []
        for path in result_paths:
            summary = self._load_result(path)
            if summary:
                runs.append(summary)
        
        if not runs:
            return ComparisonResult()
        
        # Calculate statistics
        successful = [r for r in runs if r.success]
        success_rate = len(successful) / len(runs) * 100 if runs else 0
        
        scores = [r.quality_score for r in runs if r.quality_score is not None]
        avg_quality = sum(scores) / len(scores) if scores else 0
        
        best_run = max(runs, key=lambda x: x.quality_score or 0).name if scores else None
        worst_run = min(runs, key=lambda x: x.quality_score or 100).name if scores else None
        
        # Find differences
        differences = self._find_differences(runs)
        
        result = ComparisonResult(
            runs=runs,
            differences=differences,
            best_run=best_run,
            worst_run=worst_run,
            avg_quality=avg_quality,
            success_rate=success_rate,
        )
        
        logger.info(f"Comparison complete. {len(runs)} runs, {success_rate:.0f}% success rate")
        return result
    
    def _load_result(self, path: str) -> Optional[DesignRunSummary]:
        """Load a result file and extract summary."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            
            # Extract key fields
            workflow = data.get("workflow", "unknown")
            primers = data.get("primers", {})
            qc = data.get("qc", {})
            
            fwd = primers.get("forward", {})
            rev = primers.get("reverse", {})
            
            amplicons = data.get("amplicons", [])
            product_size = amplicons[0].get("length", 0) if amplicons else 0
            
            return DesignRunSummary(
                name=Path(path).stem,
                path=path,
                workflow=workflow,
                success=bool(primers),
                quality_score=qc.get("quality_score"),
                quality_grade=qc.get("quality_category"),
                primer_count=len(primers),
                forward_seq=fwd.get("sequence", ""),
                reverse_seq=rev.get("sequence", ""),
                product_size=product_size,
                tm_forward=fwd.get("tm", 0.0),
                tm_reverse=rev.get("tm", 0.0),
            )
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
            return None
    
    def _find_differences(self, runs: List[DesignRunSummary]) -> List[Dict[str, Any]]:
        """Find significant differences between runs."""
        differences = []
        
        if len(runs) < 2:
            return differences
        
        # Compare quality scores
        scores = [(r.name, r.quality_score) for r in runs if r.quality_score]
        if scores:
            min_score = min(s[1] for s in scores)
            max_score = max(s[1] for s in scores)
            if max_score - min_score > 10:
                differences.append({
                    "type": "quality_variance",
                    "description": f"Quality score range: {min_score:.0f} - {max_score:.0f}",
                    "severity": "high" if max_score - min_score > 20 else "medium",
                })
        
        # Compare product sizes
        sizes = [(r.name, r.product_size) for r in runs if r.product_size > 0]
        if sizes:
            min_size = min(s[1] for s in sizes)
            max_size = max(s[1] for s in sizes)
            if max_size - min_size > 50:
                differences.append({
                    "type": "size_variance",
                    "description": f"Product size range: {min_size} - {max_size} bp",
                    "severity": "medium",
                })
        
        # Compare Tm
        tms = [(r.name, r.tm_forward) for r in runs if r.tm_forward > 0]
        if tms:
            min_tm = min(t[1] for t in tms)
            max_tm = max(t[1] for t in tms)
            if max_tm - min_tm > 3:
                differences.append({
                    "type": "tm_variance",
                    "description": f"Tm range: {min_tm:.1f} - {max_tm:.1f}°C",
                    "severity": "medium" if max_tm - min_tm > 5 else "low",
                })
        
        return differences


def compare_batch(result_paths: List[str]) -> ComparisonResult:
    """
    Compare multiple design runs.
    
    Args:
        result_paths: List of paths to result.json files
        
    Returns:
        ComparisonResult with comparison data
    """
    comparator = BatchComparator()
    return comparator.compare(result_paths)
