"""
Public API for PrimerLab.
This module provides a high-level programmatic interface for external applications.
"""

from typing import Dict, Any, Optional
from primerlab.core.models import WorkflowResult
from primerlab.workflows.pcr.workflow import run_pcr_workflow
from primerlab.workflows.qpcr.workflow import run_qpcr_workflow
from primerlab.core.config_loader import load_and_merge_config


def validate_primers(
    forward_primer: str,
    reverse_primer: str,
    template: str,
    template_name: str = "template",
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Run in-silico PCR validation for a primer pair.
    
    Args:
        forward_primer: Forward primer sequence (5' to 3')
        reverse_primer: Reverse primer sequence (5' to 3')
        template: Template DNA sequence
        template_name: Name for the template (default: "template")
        params: Optional in-silico parameters
        
    Returns:
        Dictionary with validation results including:
        - success: bool
        - products: list of predicted products
        - primary_product: best product if any
        - warnings: list of warnings
        - errors: list of errors
    """
    from primerlab.core.insilico import run_insilico_pcr
    
    result = run_insilico_pcr(
        template=template,
        forward_primer=forward_primer,
        reverse_primer=reverse_primer,
        template_name=template_name,
        params=params
    )
    
    # Convert to dictionary for API response
    primary = None
    if result.products:
        for p in result.products:
            if p.is_primary:
                primary = {
                    "size": p.product_size,
                    "position": f"{p.start_position}-{p.end_position}",
                    "likelihood": p.likelihood_score,
                    "sequence_preview": p.product_sequence[:50] + "..." if len(p.product_sequence) > 50 else p.product_sequence
                }
                break
    
    return {
        "success": result.success,
        "products_count": len(result.products),
        "primary_product": primary,
        "forward_bindings": len(result.all_forward_bindings),
        "reverse_bindings": len(result.all_reverse_bindings),
        "warnings": result.warnings,
        "errors": result.errors
    }


def design_pcr_primers(
    sequence: str, 
    config: Optional[Dict[str, Any]] = None,
    validate: bool = False
) -> WorkflowResult:
    """
    Programmatic entry point for PCR primer design.
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
                If provided, it merges with/overrides default PCR settings.
        validate: If True, run in-silico PCR validation after design (v0.2.3)
        
    Returns:
        WorkflowResult object containing primers and QC status.
        If validate=True, includes 'insilico_validation' in metadata.
    """
    # Base config structure
    base_config = {
        "workflow": "pcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"} # Default output for API calls
    }
    
    # Merge with user config if provided
    final_config = base_config
    if config:
        final_config.update(config)
        final_config["input"]["sequence"] = sequence

    result = run_pcr_workflow(final_config)
    
    # v0.2.3: Optional in-silico validation
    if validate and result.primers:
        fwd = result.primers.get("forward")
        rev = result.primers.get("reverse")
        
        if fwd and rev:
            validation = validate_primers(
                forward_primer=fwd.sequence,
                reverse_primer=rev.sequence,
                template=sequence,
                template_name=result.metadata.workflow if result.metadata else "template"
            )
            # Add validation to metadata
            if result.metadata:
                result.metadata.insilico_validation = validation
            else:
                # Store in result as attribute
                result.insilico_validation = validation
    
    return result


def design_qpcr_assays(
    sequence: str, 
    config: Optional[Dict[str, Any]] = None,
    validate: bool = False
) -> WorkflowResult:
    """
    Programmatic entry point for qPCR assay design (primers + probe).
    
    Args:
        sequence: DNA sequence string
        config: Optional configuration dictionary override.
        validate: If True, run in-silico PCR validation after design (v0.2.3)
        
    Returns:
        WorkflowResult object containing primers, probe, and efficiency metrics.
    """
    base_config = {
        "workflow": "qpcr",
        "input": {"sequence": sequence},
        "parameters": {},
        "output": {"directory": "primerlab_api_out"}
    }
    
    final_config = base_config
    if config:
        final_config.update(config)
        final_config["input"]["sequence"] = sequence

    result = run_qpcr_workflow(final_config)
    
    # v0.2.3: Optional in-silico validation
    if validate and result.primers:
        fwd = result.primers.get("forward")
        rev = result.primers.get("reverse")
        
        if fwd and rev:
            validation = validate_primers(
                forward_primer=fwd.sequence,
                reverse_primer=rev.sequence,
                template=sequence,
                template_name=result.metadata.workflow if result.metadata else "template"
            )
            if result.metadata:
                result.metadata.insilico_validation = validation
            else:
                result.insilico_validation = validation
    
    return result


def check_offtargets(
    forward_primer: str,
    reverse_primer: str,
    database: str,
    target_id: Optional[str] = None,
    mode: str = "auto"
) -> Dict[str, Any]:
    """
    Check primer pair for off-target binding sites (v0.3.1).
    
    Args:
        forward_primer: Forward primer sequence (5' to 3')
        reverse_primer: Reverse primer sequence (5' to 3')
        database: Path to FASTA or BLAST database
        target_id: Expected target sequence ID (optional)
        mode: Alignment mode - 'auto', 'blast', or 'biopython'
        
    Returns:
        Dictionary with:
        - specificity_score: 0-100 score
        - grade: A-F grade
        - is_specific: bool
        - forward_offtargets: count
        - reverse_offtargets: count
        - details: additional info
    """
    from primerlab.core.offtarget.finder import OfftargetFinder
    from primerlab.core.offtarget.scorer import SpecificityScorer
    
    finder = OfftargetFinder(
        database=database,
        target_id=target_id,
        mode=mode
    )
    
    result = finder.find_primer_pair_offtargets(
        forward_primer=forward_primer,
        reverse_primer=reverse_primer,
        target_id=target_id
    )
    
    scorer = SpecificityScorer()
    fwd_score, rev_score, combined = scorer.score_primer_pair(result)
    
    return {
        "specificity_score": combined.overall_score,
        "grade": combined.grade,
        "is_specific": combined.is_acceptable,
        "forward_offtargets": result.forward_result.offtarget_count,
        "reverse_offtargets": result.reverse_result.offtarget_count,
        "potential_products": result.potential_products,
        "details": {
            "forward_score": fwd_score.overall_score,
            "reverse_score": rev_score.overall_score,
            "binding_score": combined.binding_score,
            "mismatch_score": combined.mismatch_score
        }
    }


def check_primer_compatibility(
    primers: list[Dict[str, str]],
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Check compatibility of multiple primer pairs for multiplexing.
    
    Args:
        primers: List of dictionaries representing primer pairs.
                 Each dict must have: 'name', 'fwd', 'rev'.
                 Optional keys: 'tm_fwd', 'tm_rev', 'gc_fwd', 'gc_rev'.
        config: Optional configuration dictionary override.
        
    Returns:
        Dictionary with:
        - is_valid: bool
        - score: 0-100 float
        - grade: A-F string
        - matrix: interaction details
        - warnings: list of specific issues
        - recommendations: list of suggestions
    """
    from primerlab.core.compat_check.models import MultiplexPair
    from primerlab.core.compat_check.dimer import DimerEngine
    from primerlab.core.compat_check.scoring import MultiplexScorer
    from primerlab.core.compat_check.validator import MultiplexValidator
    from primerlab.core.config_loader import load_and_merge_config
    
    # Load config
    full_config = load_and_merge_config("compat_check", cli_overrides=config)
    
    # Map input to MultiplexPair models
    mapped_primers = []
    for p in primers:
        mp = MultiplexPair(
            name=p.get('name', f"Pair_{len(mapped_primers)+1}"),
            forward=p.get('fwd', p.get('forward', '')),
            reverse=p.get('rev', p.get('reverse', '')),
            tm_forward=p.get('tm_fwd', p.get('tm_forward', 0.0)),
            tm_reverse=p.get('tm_rev', p.get('tm_reverse', 0.0)),
            gc_forward=p.get('gc_fwd', p.get('gc_forward', 0.0)),
            gc_reverse=p.get('gc_rev', p.get('gc_reverse', 0.0))
        )
        mapped_primers.append(mp)
        
    # 1. Calculate Dimers
    engine = DimerEngine()
    matrix = engine.build_matrix(mapped_primers)
    
    # 2. Score
    scorer = MultiplexScorer(full_config)
    score_result = scorer.calculate_score(matrix, mapped_primers)
    
    # 3. Validate
    validator = MultiplexValidator(full_config)
    validation_summary = validator.get_validation_summary(matrix, mapped_primers)
    
    return {
        "is_valid": validation_summary["is_valid"],
        "score": score_result.score,
        "grade": score_result.grade,
        "pair_count": len(mapped_primers),
        "component_scores": score_result.component_scores,
        "warnings": validation_summary["warnings"] + score_result.warnings,
        "errors": validation_summary["errors"],
        "recommendations": score_result.recommendations
    }


def analyze_amplicon(
    sequence: str,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analyze an amplicon sequence for quality metrics (v0.4.1).
    
    Args:
        sequence: Amplicon DNA sequence
        config: Optional configuration dictionary override.
        
    Returns:
        Dictionary containing:
        - quality_score: overall score (0-100)
        - grade: letter grade (A-F)
        - secondary_structure: structure prediction results
        - gc_profile: GC content analysis
        - gc_clamp: end analysis
        - amplicon_tm: predicted melting temperature
        - warnings: list of quality issues
    """
    from primerlab.core.amplicon import analyze_amplicon as _analyze
    
    # Load config if provided
    full_config = config or {}
    
    # Run analysis
    result = _analyze(sequence, full_config)
    
    return {
        "length": result.length,
        "quality_score": result.quality.score if result.quality else None,
        "grade": result.quality.grade if result.quality else None,
        "secondary_structure": result.secondary_structure.to_dict() if result.secondary_structure else None,
        "gc_profile": result.gc_profile.to_dict() if result.gc_profile else None,
        "gc_clamp": result.gc_clamp.to_dict() if result.gc_clamp else None,
        "amplicon_tm": result.amplicon_tm.to_dict() if result.amplicon_tm else None,
        "warnings": result.quality.warnings if result.quality else []
    }


def run_overlap_simulation(
    template: str,
    primer_pairs: list[Dict[str, str]],
    template_name: str = "template",
    min_overlap_warning: int = 50
) -> Dict[str, Any]:
    """
    Run in-silico overlap simulation for multiple primer pairs (v0.4.1).
    
    Args:
        template: Template DNA sequence
        primer_pairs: List of primer pair dicts with 'name', 'forward', 'reverse' keys
        template_name: Name for the template
        min_overlap_warning: Minimum overlap (bp) to flag as problematic
        
    Returns:
        Dictionary containing:
        - template_length: length of template
        - amplicons: list of predicted amplicons
        - overlaps: list of detected overlaps
        - has_problems: True if problematic overlaps detected
        - warnings: list of warnings
    """
    from primerlab.core.compat_check.overlap_detection import run_insilico_compat_simulation
    
    result = run_insilico_compat_simulation(
        template=template,
        primer_pairs=primer_pairs,
        template_name=template_name,
        min_overlap_warning=min_overlap_warning
    )
    
    return result.to_dict()


def check_species_specificity_api(
    primers: list[Dict[str, str]],
    target_template: str,
    target_name: str = "target",
    offtarget_templates: Optional[Dict[str, str]] = None,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Check primer specificity across multiple species (v0.4.2).
    
    Args:
        primers: List of primer dicts with 'name', 'forward', 'reverse' keys
        target_template: Target species template sequence
        target_name: Name for target species
        offtarget_templates: Dict mapping species_name -> template sequence
        config: Optional configuration dict
        
    Returns:
        Dictionary containing:
        - overall_score: specificity score (0-100)
        - grade: letter grade (A-F)
        - is_specific: True if all primers specific to target
        - warnings: list of off-target binding warnings
        - matrix: specificity matrix data
    """
    from primerlab.core.species import (
        SpeciesTemplate,
        check_species_specificity as _check
    )
    
    # Create template objects
    target = SpeciesTemplate(
        species_name=target_name,
        sequence=target_template
    )
    
    offtargets = {}
    if offtarget_templates:
        for name, seq in offtarget_templates.items():
            offtargets[name] = SpeciesTemplate(species_name=name, sequence=seq)
    
    # Run check
    result = _check(primers, target, offtargets, config)
    
    return result.to_dict()
