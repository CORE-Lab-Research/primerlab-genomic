"""
Transcript Loader (v0.6.0).

Loads transcript annotations from GTF/BED files for exon boundary detection.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from pathlib import Path


@dataclass
class Exon:
    """Single exon definition."""
    
    exon_number: int
    start: int  # 0-indexed
    end: int    # Exclusive
    
    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class Transcript:
    """Transcript with exon structure."""
    
    transcript_id: str
    gene_name: str
    chromosome: str
    strand: str  # '+' or '-'
    
    exons: List[Exon] = field(default_factory=list)
    
    @property
    def exon_count(self) -> int:
        return len(self.exons)
    
    @property
    def cds_length(self) -> int:
        """Total length of coding sequence (all exons)."""
        return sum(e.length for e in self.exons)
    
    def get_exon_boundaries(self) -> List[Tuple[int, int]]:
        """Get list of (start, end) for each exon in transcript coordinates."""
        boundaries = []
        current_pos = 0
        
        for exon in sorted(self.exons, key=lambda e: e.exon_number):
            boundaries.append((current_pos, current_pos + exon.length))
            current_pos += exon.length
        
        return boundaries
    
    def get_junction_positions(self) -> List[int]:
        """Get positions of exon-exon junctions in transcript coordinates."""
        junctions = []
        current_pos = 0
        
        for i, exon in enumerate(sorted(self.exons, key=lambda e: e.exon_number)):
            current_pos += exon.length
            if i < len(self.exons) - 1:  # Not last exon
                junctions.append(current_pos)
        
        return junctions
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "transcript_id": self.transcript_id,
            "gene_name": self.gene_name,
            "chromosome": self.chromosome,
            "strand": self.strand,
            "exon_count": self.exon_count,
            "cds_length": self.cds_length,
            "junctions": self.get_junction_positions(),
        }


def parse_gtf_line(line: str) -> Optional[Dict]:
    """
    Parse a single GTF line.
    
    Args:
        line: GTF format line
        
    Returns:
        Dict with parsed fields or None if not an exon
    """
    if line.startswith("#"):
        return None
    
    parts = line.strip().split("\t")
    if len(parts) < 9:
        return None
    
    feature = parts[2]
    if feature != "exon":
        return None
    
    # Parse attributes
    attrs = {}
    for attr in parts[8].split(";"):
        attr = attr.strip()
        if not attr:
            continue
        
        if " " in attr:
            key, value = attr.split(" ", 1)
            attrs[key] = value.strip('"')
    
    return {
        "chromosome": parts[0],
        "start": int(parts[3]) - 1,  # Convert to 0-indexed
        "end": int(parts[4]),
        "strand": parts[6],
        "transcript_id": attrs.get("transcript_id", ""),
        "gene_name": attrs.get("gene_name", attrs.get("gene_id", "")),
        "exon_number": int(attrs.get("exon_number", 1)),
    }


def load_transcript_bed(
    bed_path: str,
    transcript_id: Optional[str] = None,
) -> List[Transcript]:
    """
    Load transcripts from BED12 format file.
    
    BED12 columns:
    1. chrom
    2. chromStart
    3. chromEnd
    4. name (transcript ID)
    5. score
    6. strand
    7. thickStart
    8. thickEnd
    9. itemRgb
    10. blockCount (exon count)
    11. blockSizes (comma-separated exon sizes)
    12. blockStarts (comma-separated exon starts relative to chromStart)
    
    Args:
        bed_path: Path to BED12 file
        transcript_id: Optional filter by transcript ID
        
    Returns:
        List of Transcript objects
    """
    transcripts = []
    
    path = Path(bed_path)
    if not path.exists():
        return []
    
    with open(path, 'r') as f:
        for line in f:
            if line.startswith("#") or line.startswith("track"):
                continue
            
            parts = line.strip().split("\t")
            if len(parts) < 12:
                continue
            
            tid = parts[3]
            if transcript_id and tid != transcript_id:
                continue
            
            chrom = parts[0]
            chrom_start = int(parts[1])
            strand = parts[5]
            block_count = int(parts[9])
            block_sizes = [int(x) for x in parts[10].rstrip(",").split(",") if x]
            block_starts = [int(x) for x in parts[11].rstrip(",").split(",") if x]
            
            # Build exons
            exons = []
            for i in range(block_count):
                exon_start = chrom_start + block_starts[i]
                exon_end = exon_start + block_sizes[i]
                exons.append(Exon(
                    exon_number=i + 1,
                    start=exon_start,
                    end=exon_end,
                ))
            
            transcript = Transcript(
                transcript_id=tid,
                gene_name=parts[3].split(".")[0] if "." in parts[3] else parts[3],
                chromosome=chrom,
                strand=strand,
                exons=exons,
            )
            
            transcripts.append(transcript)
    
    return transcripts
