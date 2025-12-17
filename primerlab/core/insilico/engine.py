"""
Virtual PCR Engine (v0.2.0)

Core engine for in-silico PCR simulation.
Simulates primer binding and amplicon prediction.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from pathlib import Path

from primerlab.core.logger import get_logger

logger = get_logger()


# Default parameters
DEFAULT_INSILICO_PARAMS = {
    # Binding requirements
    "min_3prime_match": 3,          # bp perfect match at 3' end
    "max_5prime_mismatch": 2,       # max mismatches at 5' end
    "min_total_match_percent": 80,  # minimum % identity
    "three_prime_dg_max": -2.0,     # max ΔG at 3' end (kcal/mol)
    
    # Temperature parameters
    "annealing_temp": None,         # None = auto (Tm - 5°C)
    "annealing_temp_range": [50, 72],
    
    # Salt conditions (mM)
    "na_conc": 50,
    "mg_conc": 2.0,
    "dntp_conc": 0.2,
    
    # Extension parameters
    "extension_time": None,         # None = auto (1min/kb)
    "max_amplicon_for_extension": 3000,
    
    # Product filtering
    "product_size_min": 50,
    "product_size_max": 10000,
    "max_products": 10,
    "report_threshold": 70,         # min match % to report
}


@dataclass
class PrimerBinding:
    """Represents a primer binding site on the template."""
    primer_name: str
    primer_seq: str
    strand: str                     # '+' or '-'
    position: int                   # 0-indexed start position on template
    match_percent: float            # overall match percentage
    mismatches: int                 # total mismatches
    three_prime_match: int          # perfect match bp at 3' end
    binding_tm: float               # calculated Tm at binding site
    is_valid: bool                  # meets minimum requirements
    alignment: str = ""             # visual alignment string


@dataclass  
class AmpliconPrediction:
    """Represents a predicted PCR product."""
    forward_binding: PrimerBinding
    reverse_binding: PrimerBinding
    product_size: int
    product_sequence: str
    start_position: int
    end_position: int
    likelihood_score: float         # 0-100 based on binding quality
    is_primary: bool = False        # primary (best) product
    warnings: List[str] = field(default_factory=list)


@dataclass
class InsilicoPCRResult:
    """Complete result of in-silico PCR simulation."""
    success: bool
    template_name: str
    template_length: int
    forward_primer: str
    reverse_primer: str
    products: List[AmpliconPrediction]
    all_forward_bindings: List[PrimerBinding]
    all_reverse_bindings: List[PrimerBinding]
    parameters: Dict[str, Any]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def reverse_complement(seq: str) -> str:
    """Return reverse complement of DNA sequence."""
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 
                  'a': 't', 't': 'a', 'g': 'c', 'c': 'g',
                  'N': 'N', 'n': 'n'}
    return ''.join(complement.get(base, 'N') for base in reversed(seq))


def calculate_match_percent(primer: str, target: str) -> Tuple[float, int, int]:
    """
    Calculate match percentage between primer and target.
    
    Returns:
        Tuple of (match_percent, total_mismatches, three_prime_matches)
    """
    if len(primer) != len(target):
        # Pad shorter sequence
        max_len = max(len(primer), len(target))
        primer = primer.ljust(max_len, 'N')
        target = target.ljust(max_len, 'N')
    
    matches = sum(1 for p, t in zip(primer.upper(), target.upper()) if p == t)
    mismatches = len(primer) - matches
    match_percent = (matches / len(primer)) * 100
    
    # Count 3' end perfect match (from 3' end of primer)
    three_prime_match = 0
    for p, t in zip(reversed(primer.upper()), reversed(target.upper())):
        if p == t:
            three_prime_match += 1
        else:
            break
    
    return match_percent, mismatches, three_prime_match


def find_binding_sites(
    primer_seq: str,
    template_seq: str,
    primer_name: str,
    strand: str,
    params: Dict[str, Any]
) -> List[PrimerBinding]:
    """
    Find all potential binding sites for a primer on the template.
    
    Args:
        primer_seq: Primer sequence (5' to 3')
        template_seq: Template sequence
        primer_name: Name of the primer
        strand: '+' for forward, '-' for reverse
        params: In-silico parameters
        
    Returns:
        List of PrimerBinding objects
    """
    bindings = []
    primer_len = len(primer_seq)
    primer_upper = primer_seq.upper()
    
    # For reverse primer, we look for binding to the reverse complement
    if strand == '-':
        search_seq = reverse_complement(primer_upper)
    else:
        search_seq = primer_upper
    
    template_upper = template_seq.upper()
    
    # Slide along template looking for potential binding sites
    for i in range(len(template_upper) - primer_len + 1):
        target_region = template_upper[i:i + primer_len]
        
        match_pct, mismatches, three_prime_match = calculate_match_percent(
            search_seq, target_region
        )
        
        # Check if this site meets minimum threshold for reporting
        if match_pct >= params.get("report_threshold", 70):
            # Validate against binding requirements
            is_valid = (
                match_pct >= params.get("min_total_match_percent", 80) and
                three_prime_match >= params.get("min_3prime_match", 3) and
                mismatches <= primer_len - params.get("min_3prime_match", 3) + params.get("max_5prime_mismatch", 2)
            )
            
            # TODO: Calculate binding Tm using ViennaRNA
            binding_tm = 60.0  # Placeholder
            
            # Create alignment string
            alignment = create_alignment_string(search_seq, target_region)
            
            binding = PrimerBinding(
                primer_name=primer_name,
                primer_seq=primer_seq,
                strand=strand,
                position=i,
                match_percent=match_pct,
                mismatches=mismatches,
                three_prime_match=three_prime_match,
                binding_tm=binding_tm,
                is_valid=is_valid,
                alignment=alignment
            )
            bindings.append(binding)
    
    # Sort by match quality (best first)
    bindings.sort(key=lambda b: (-b.match_percent, -b.three_prime_match))
    
    return bindings


def create_alignment_string(primer: str, target: str) -> str:
    """Create visual alignment string showing matches/mismatches."""
    alignment = []
    for p, t in zip(primer.upper(), target.upper()):
        if p == t:
            alignment.append('|')
        else:
            alignment.append('x')
    return ''.join(alignment)


def predict_products(
    forward_bindings: List[PrimerBinding],
    reverse_bindings: List[PrimerBinding],
    template_seq: str,
    params: Dict[str, Any]
) -> List[AmpliconPrediction]:
    """
    Predict PCR products from forward and reverse binding sites.
    
    A valid product requires:
    - Forward primer on + strand
    - Reverse primer on - strand (binds to complement)
    - Reverse primer downstream of forward primer
    - Product size within range
    """
    products = []
    
    min_size = params.get("product_size_min", 50)
    max_size = params.get("product_size_max", 10000)
    max_products = params.get("max_products", 10)
    
    for fwd in forward_bindings:
        if not fwd.is_valid:
            continue
            
        for rev in reverse_bindings:
            if not rev.is_valid:
                continue
            
            # Calculate product size
            # Forward primer starts at fwd.position
            # Reverse primer's 3' end is at rev.position (on the reverse strand)
            # Product includes both primers
            fwd_start = fwd.position
            rev_end = rev.position + len(rev.primer_seq)
            
            product_size = rev_end - fwd_start
            
            # Skip if wrong orientation or size
            if product_size < min_size or product_size > max_size:
                continue
            
            # Extract product sequence
            product_seq = template_seq[fwd_start:rev_end]
            
            # Calculate likelihood score (average of binding qualities)
            likelihood = (fwd.match_percent + rev.match_percent) / 2
            
            # Check for warnings
            warnings = []
            if product_size > params.get("max_amplicon_for_extension", 3000):
                warnings.append(f"Long amplicon ({product_size}bp) may need extended extension time")
            
            product = AmpliconPrediction(
                forward_binding=fwd,
                reverse_binding=rev,
                product_size=product_size,
                product_sequence=product_seq,
                start_position=fwd_start,
                end_position=rev_end,
                likelihood_score=likelihood,
                warnings=warnings
            )
            products.append(product)
    
    # Sort by likelihood (best first)
    products.sort(key=lambda p: -p.likelihood_score)
    
    # Mark primary product
    if products:
        products[0].is_primary = True
    
    # Limit to max products
    return products[:max_products]


class InsilicoPCR:
    """
    In-silico PCR simulation engine.
    
    Simulates PCR amplification by predicting primer binding sites
    and resulting products.
    """
    
    def __init__(self, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the engine with parameters.
        
        Args:
            params: Custom parameters (merged with defaults)
        """
        self.params = {**DEFAULT_INSILICO_PARAMS}
        if params:
            self.params.update(params)
    
    def run(
        self,
        template: str,
        forward_primer: str,
        reverse_primer: str,
        template_name: str = "template"
    ) -> InsilicoPCRResult:
        """
        Run in-silico PCR simulation.
        
        Args:
            template: Template sequence (DNA)
            forward_primer: Forward primer sequence (5' to 3')
            reverse_primer: Reverse primer sequence (5' to 3')
            template_name: Name for the template
            
        Returns:
            InsilicoPCRResult with all predictions
        """
        logger.info(f"Running in-silico PCR on {template_name}")
        
        warnings = []
        errors = []
        
        # Validate inputs
        if len(template) < 50:
            errors.append("Template sequence too short (< 50bp)")
            return InsilicoPCRResult(
                success=False,
                template_name=template_name,
                template_length=len(template),
                forward_primer=forward_primer,
                reverse_primer=reverse_primer,
                products=[],
                all_forward_bindings=[],
                all_reverse_bindings=[],
                parameters=self.params,
                errors=errors
            )
        
        # Find forward primer binding sites (+ strand)
        logger.debug("Finding forward primer binding sites...")
        forward_bindings = find_binding_sites(
            primer_seq=forward_primer,
            template_seq=template,
            primer_name="Forward",
            strand='+',
            params=self.params
        )
        
        if not forward_bindings:
            warnings.append("No forward primer binding sites found")
        else:
            valid_fwd = sum(1 for b in forward_bindings if b.is_valid)
            logger.info(f"Found {len(forward_bindings)} forward binding sites ({valid_fwd} valid)")
        
        # Find reverse primer binding sites (- strand)
        logger.debug("Finding reverse primer binding sites...")
        reverse_bindings = find_binding_sites(
            primer_seq=reverse_primer,
            template_seq=template,
            primer_name="Reverse",
            strand='-',
            params=self.params
        )
        
        if not reverse_bindings:
            warnings.append("No reverse primer binding sites found")
        else:
            valid_rev = sum(1 for b in reverse_bindings if b.is_valid)
            logger.info(f"Found {len(reverse_bindings)} reverse binding sites ({valid_rev} valid)")
        
        # Predict products
        products = predict_products(
            forward_bindings=forward_bindings,
            reverse_bindings=reverse_bindings,
            template_seq=template,
            params=self.params
        )
        
        if not products:
            warnings.append("No valid products predicted")
        else:
            logger.info(f"Predicted {len(products)} products")
            if len(products) > 1:
                warnings.append(f"Multiple products ({len(products)}) - potential non-specific amplification")
        
        success = len(products) > 0 and not errors
        
        return InsilicoPCRResult(
            success=success,
            template_name=template_name,
            template_length=len(template),
            forward_primer=forward_primer,
            reverse_primer=reverse_primer,
            products=products,
            all_forward_bindings=forward_bindings,
            all_reverse_bindings=reverse_bindings,
            parameters=self.params,
            warnings=warnings,
            errors=errors
        )


def run_insilico_pcr(
    template: str,
    forward_primer: str,
    reverse_primer: str,
    template_name: str = "template",
    params: Optional[Dict[str, Any]] = None
) -> InsilicoPCRResult:
    """
    Convenience function to run in-silico PCR.
    
    Args:
        template: Template sequence
        forward_primer: Forward primer (5' to 3')
        reverse_primer: Reverse primer (5' to 3')
        template_name: Name for template
        params: Optional custom parameters
        
    Returns:
        InsilicoPCRResult
    """
    engine = InsilicoPCR(params)
    return engine.run(template, forward_primer, reverse_primer, template_name)
