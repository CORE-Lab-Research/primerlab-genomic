"""
BED Parser (v0.3.1)

Parse BED files for genomic region filtering.
"""

from pathlib import Path
from typing import List, Tuple, Optional, Iterator
from dataclasses import dataclass


@dataclass
class BEDRegion:
    """
    Represents a BED region.
    
    Attributes:
        chrom: Chromosome name
        start: Start position (0-based)
        end: End position (exclusive)
        name: Optional region name
        score: Optional score
        strand: Optional strand (+ or -)
    """
    chrom: str
    start: int
    end: int
    name: Optional[str] = None
    score: Optional[float] = None
    strand: Optional[str] = None
    
    @property
    def length(self) -> int:
        """Region length in bp."""
        return self.end - self.start
    
    def contains(self, pos: int) -> bool:
        """Check if position is within region (1-based input)."""
        return self.start < pos <= self.end
    
    def overlaps(self, start: int, end: int) -> bool:
        """Check if region overlaps with another (1-based input)."""
        return not (end <= self.start or start >= self.end)


class BEDParser:
    """
    Parser for BED format files.
    
    Supports BED3, BED6, and custom columns.
    """
    
    def __init__(self, bed_path: str):
        """
        Initialize BED parser.
        
        Args:
            bed_path: Path to BED file
        """
        self.bed_path = Path(bed_path)
        self._validate_file()
    
    def _validate_file(self):
        """Validate BED file exists."""
        if not self.bed_path.exists():
            raise FileNotFoundError(f"BED file not found: {self.bed_path}")
    
    def parse(self, chrom: Optional[str] = None) -> Iterator[BEDRegion]:
        """
        Parse BED file and yield regions.
        
        Args:
            chrom: Filter by chromosome (optional)
            
        Yields:
            BEDRegion objects
        """
        with open(self.bed_path) as f:
            for line in f:
                line = line.strip()
                
                # Skip headers and comments
                if not line or line.startswith('#') or line.startswith('track') or line.startswith('browser'):
                    continue
                
                region = self._parse_line(line)
                if region is None:
                    continue
                
                # Filter by chromosome
                if chrom and region.chrom != chrom:
                    continue
                
                yield region
    
    def _parse_line(self, line: str) -> Optional[BEDRegion]:
        """Parse a single BED line."""
        cols = line.split('\t')
        if len(cols) < 3:
            return None
        
        try:
            chrom = cols[0]
            start = int(cols[1])
            end = int(cols[2])
            
            name = cols[3] if len(cols) > 3 and cols[3] != '.' else None
            
            score = None
            if len(cols) > 4 and cols[4] != '.':
                try:
                    score = float(cols[4])
                except ValueError:
                    pass
            
            strand = cols[5] if len(cols) > 5 and cols[5] in ('+', '-') else None
            
            return BEDRegion(
                chrom=chrom,
                start=start,
                end=end,
                name=name,
                score=score,
                strand=strand
            )
        except (ValueError, IndexError):
            return None
    
    def get_regions(self, chrom: Optional[str] = None) -> List[BEDRegion]:
        """Get all regions as list."""
        return list(self.parse(chrom))
    
    def filter_positions(
        self,
        chrom: str,
        positions: List[int]
    ) -> List[int]:
        """
        Filter positions that fall within BED regions.
        
        Args:
            chrom: Chromosome
            positions: List of 1-based positions
            
        Returns:
            Positions that are within any region
        """
        regions = self.get_regions(chrom)
        return [p for p in positions if any(r.contains(p) for r in regions)]


def parse_bed(bed_path: str, chrom: Optional[str] = None) -> List[BEDRegion]:
    """
    Convenience function to parse BED file.
    
    Args:
        bed_path: Path to BED file
        chrom: Filter by chromosome
        
    Returns:
        List of BEDRegion objects
    """
    parser = BEDParser(bed_path)
    return parser.get_regions(chrom)
