"""
VCF Parser (v0.3.1)

Parse VCF files for variant information.
Supports VCF 4.x format, optional gzip compression.
"""

import gzip
from pathlib import Path
from typing import List, Optional, Iterator, Tuple
from dataclasses import dataclass

from primerlab.core.models.variant import Variant, VariantType


@dataclass
class VCFHeader:
    """VCF file header information."""
    version: str = "4.0"
    samples: List[str] = None
    contigs: List[str] = None
    info_fields: dict = None
    
    def __post_init__(self):
        self.samples = self.samples or []
        self.contigs = self.contigs or []
        self.info_fields = self.info_fields or {}


class VCFParser:
    """
    Parser for VCF (Variant Call Format) files.
    
    Supports:
    - VCF 4.x format
    - Gzip compressed files (.vcf.gz)
    - Region filtering
    - MAF filtering
    """
    
    def __init__(self, vcf_path: str):
        """
        Initialize VCF parser.
        
        Args:
            vcf_path: Path to VCF file (.vcf or .vcf.gz)
        """
        self.vcf_path = Path(vcf_path)
        self.is_gzipped = self.vcf_path.suffix == '.gz' or str(self.vcf_path).endswith('.vcf.gz')
        self.header = None
        self._validate_file()
    
    def _validate_file(self):
        """Validate VCF file exists."""
        if not self.vcf_path.exists():
            raise FileNotFoundError(f"VCF file not found: {self.vcf_path}")
    
    def _open_file(self):
        """Open file with appropriate handler."""
        if self.is_gzipped:
            return gzip.open(self.vcf_path, 'rt')
        return open(self.vcf_path, 'r')
    
    def parse_header(self) -> VCFHeader:
        """Parse VCF header and return metadata."""
        header = VCFHeader()
        
        with self._open_file() as f:
            for line in f:
                line = line.strip()
                if line.startswith('##'):
                    # Meta-information line
                    if line.startswith('##fileformat='):
                        header.version = line.split('=')[1]
                    elif line.startswith('##contig='):
                        # Extract contig ID
                        try:
                            contig_id = line.split('ID=')[1].split(',')[0].rstrip('>')
                            header.contigs.append(contig_id)
                        except IndexError:
                            pass
                elif line.startswith('#CHROM'):
                    # Column header line
                    cols = line.split('\t')
                    if len(cols) > 9:
                        header.samples = cols[9:]
                    break
        
        self.header = header
        return header
    
    def parse(
        self,
        chrom: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        min_maf: Optional[float] = None,
        max_maf: Optional[float] = None
    ) -> Iterator[Variant]:
        """
        Parse VCF file and yield variants.
        
        Args:
            chrom: Filter by chromosome
            start: Filter by start position (1-based)
            end: Filter by end position
            min_maf: Minimum MAF threshold
            max_maf: Maximum MAF threshold
            
        Yields:
            Variant objects
        """
        with self._open_file() as f:
            for line in f:
                line = line.strip()
                
                # Skip headers
                if line.startswith('#'):
                    continue
                
                # Parse variant line
                variant = self._parse_line(line)
                if variant is None:
                    continue
                
                # Apply filters
                if chrom and variant.chrom != chrom:
                    continue
                
                if start and variant.pos < start:
                    continue
                
                if end and variant.pos > end:
                    continue
                
                if min_maf is not None and variant.maf is not None:
                    if variant.maf < min_maf:
                        continue
                
                if max_maf is not None and variant.maf is not None:
                    if variant.maf > max_maf:
                        continue
                
                yield variant
    
    def _parse_line(self, line: str) -> Optional[Variant]:
        """
        Parse a single VCF line into a Variant.
        
        VCF columns: CHROM, POS, ID, REF, ALT, QUAL, FILTER, INFO, [FORMAT, SAMPLES...]
        """
        cols = line.split('\t')
        if len(cols) < 8:
            return None
        
        chrom = cols[0]
        
        try:
            pos = int(cols[1])
        except ValueError:
            return None
        
        rsid = cols[2] if cols[2] != '.' else None
        ref = cols[3]
        alt = cols[4].split(',')[0]  # Take first alt allele
        
        # Parse INFO field for MAF
        info = self._parse_info(cols[7])
        maf = info.get('AF') or info.get('MAF')
        
        if maf is not None:
            try:
                maf = float(maf.split(',')[0]) if isinstance(maf, str) else float(maf)
            except (ValueError, AttributeError):
                maf = None
        
        return Variant(
            chrom=chrom,
            pos=pos,
            ref=ref,
            alt=alt,
            rsid=rsid,
            maf=maf,
            info=info
        )
    
    def _parse_info(self, info_str: str) -> dict:
        """Parse INFO field into dictionary."""
        info = {}
        if info_str == '.' or not info_str:
            return info
        
        for item in info_str.split(';'):
            if '=' in item:
                key, value = item.split('=', 1)
                info[key] = value
            else:
                info[item] = True
        
        return info
    
    def get_variants_in_region(
        self,
        chrom: str,
        start: int,
        end: int
    ) -> List[Variant]:
        """
        Get all variants in a genomic region.
        
        Args:
            chrom: Chromosome name
            start: Start position (1-based)
            end: End position
            
        Returns:
            List of variants in the region
        """
        return list(self.parse(chrom=chrom, start=start, end=end))
    
    def count_variants(self) -> int:
        """Count total variants in file."""
        count = 0
        for _ in self.parse():
            count += 1
        return count


def parse_vcf(vcf_path: str, **kwargs) -> List[Variant]:
    """
    Convenience function to parse VCF file.
    
    Args:
        vcf_path: Path to VCF file
        **kwargs: Filter arguments (chrom, start, end, min_maf, max_maf)
        
    Returns:
        List of Variant objects
    """
    parser = VCFParser(vcf_path)
    return list(parser.parse(**kwargs))
