"""
Primer Variant Check (v0.3.1)

Check primer binding sites for overlapping genetic variants (SNPs, indels).
"""

from typing import List, Optional, Tuple
from dataclasses import dataclass

from primerlab.core.models.variant import (
    Variant,
    VariantOverlap,
    VariantImpact,
    PrimerVariantResult,
    PrimerPairVariantResult
)
from primerlab.core.tools.vcf_parser import VCFParser


class VariantChecker:
    """
    Check primers for overlapping genetic variants.
    
    Detects variants that overlap with primer binding sites
    and assesses their impact on primer function.
    """
    
    def __init__(
        self,
        vcf_path: str,
        min_maf: Optional[float] = None,
        max_maf: Optional[float] = None
    ):
        """
        Initialize variant checker.
        
        Args:
            vcf_path: Path to VCF file
            min_maf: Minimum MAF to consider (filter rare variants)
            max_maf: Maximum MAF to consider
        """
        self.vcf_parser = VCFParser(vcf_path)
        self.min_maf = min_maf
        self.max_maf = max_maf
        self._variants_cache = {}
    
    def check_primer(
        self,
        primer_seq: str,
        chrom: str,
        start: int,
        end: Optional[int] = None,
        strand: str = "+",
        primer_id: str = "primer"
    ) -> PrimerVariantResult:
        """
        Check a single primer for overlapping variants.
        
        Args:
            primer_seq: Primer sequence
            chrom: Chromosome
            start: Genomic start position (1-based)
            end: Genomic end position (default: start + len - 1)
            strand: Strand (+ or -)
            primer_id: Primer identifier
            
        Returns:
            PrimerVariantResult with overlapping variants
        """
        if end is None:
            end = start + len(primer_seq) - 1
        
        # Get variants in region
        variants = self._get_variants(chrom, start, end)
        
        # Find overlaps
        overlaps = []
        for var in variants:
            if var.overlaps(start, end):
                overlap = self._create_overlap(var, start, end, strand, len(primer_seq))
                overlaps.append(overlap)
        
        return PrimerVariantResult(
            primer_id=primer_id,
            primer_seq=primer_seq,
            primer_start=start,
            primer_end=end,
            strand=strand,
            overlaps=overlaps
        )
    
    def check_primer_pair(
        self,
        forward_seq: str,
        reverse_seq: str,
        fwd_chrom: str,
        fwd_start: int,
        rev_chrom: str,
        rev_start: int,
        fwd_strand: str = "+",
        rev_strand: str = "-"
    ) -> PrimerPairVariantResult:
        """
        Check both primers in a pair for variants.
        
        Args:
            forward_seq: Forward primer sequence
            reverse_seq: Reverse primer sequence
            fwd_chrom: Forward primer chromosome
            fwd_start: Forward primer start position
            rev_chrom: Reverse primer chromosome
            rev_start: Reverse primer start position
            fwd_strand: Forward strand (default: +)
            rev_strand: Reverse strand (default: -)
            
        Returns:
            PrimerPairVariantResult
        """
        fwd_result = self.check_primer(
            primer_seq=forward_seq,
            chrom=fwd_chrom,
            start=fwd_start,
            strand=fwd_strand,
            primer_id="forward"
        )
        
        rev_result = self.check_primer(
            primer_seq=reverse_seq,
            chrom=rev_chrom,
            start=rev_start,
            strand=rev_strand,
            primer_id="reverse"
        )
        
        return PrimerPairVariantResult(
            forward_result=fwd_result,
            reverse_result=rev_result
        )
    
    def _get_variants(self, chrom: str, start: int, end: int) -> List[Variant]:
        """Get variants in region, with caching."""
        cache_key = (chrom, start, end)
        
        if cache_key not in self._variants_cache:
            self._variants_cache[cache_key] = self.vcf_parser.get_variants_in_region(
                chrom=chrom,
                start=start,
                end=end
            )
        
        return self._variants_cache[cache_key]
    
    def _create_overlap(
        self,
        variant: Variant,
        primer_start: int,
        primer_end: int,
        strand: str,
        primer_len: int
    ) -> VariantOverlap:
        """Create VariantOverlap with position calculations."""
        # Position within primer (0-based from 5')
        if strand == "+":
            primer_position = variant.pos - primer_start
            distance_from_3prime = primer_end - variant.pos
        else:
            primer_position = primer_end - variant.pos
            distance_from_3prime = variant.pos - primer_start
        
        # Clamp to valid range
        primer_position = max(0, min(primer_position, primer_len - 1))
        distance_from_3prime = max(0, distance_from_3prime)
        
        return VariantOverlap(
            variant=variant,
            primer_position=primer_position,
            distance_from_3prime=distance_from_3prime
        )


def check_variants(
    primer_seq: str,
    vcf_path: str,
    chrom: str,
    start: int,
    end: Optional[int] = None,
    min_maf: Optional[float] = None
) -> PrimerVariantResult:
    """
    Convenience function to check a primer for variants.
    
    Args:
        primer_seq: Primer sequence
        vcf_path: Path to VCF file
        chrom: Chromosome
        start: Genomic start position
        end: End position (optional)
        min_maf: Minimum MAF filter
        
    Returns:
        PrimerVariantResult
    """
    checker = VariantChecker(vcf_path, min_maf=min_maf)
    return checker.check_primer(primer_seq, chrom, start, end)
