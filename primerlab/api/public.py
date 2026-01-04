"""
Public API for PrimerLab.
This module provides a high-level programmatic interface for external applications.
"""

from typing import Dict, Any, Optional, List, Tuple
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
        
    Example:
        >>> from primerlab.api import validate_primers
        >>> result = validate_primers(
        ...     forward_primer="ATGCGATCGATCGATCG",
        ...     reverse_primer="GCTAGCTAGCTAGCTAG",
        ...     template="ATGCGATCGATCGATCG...GCTAGCTAGCTAGCTAG"
        ... )
        >>> print(result["success"])
        True
        >>> print(result["products_count"])
        1
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
        
    Example:
        >>> from primerlab.api import design_pcr_primers
        >>> result = design_pcr_primers(
        ...     sequence="ATGCGATCGATCGATCG...",
        ...     validate=True
        ... )
        >>> print(result.success)
        True
        >>> print(result.primers["forward"].sequence)
        'ATGCGATCGATCGATCG'
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
        input_dict = final_config["input"]
        if isinstance(input_dict, dict):
            input_dict["sequence"] = sequence

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
        
    Example:
        >>> from primerlab.api import design_qpcr_assays
        >>> result = design_qpcr_assays(sequence="ATGCGATCGATCGATCG...")
        >>> print(result.success)
        True
        >>> print(result.primers["probe"].sequence)
        'CGATCGATCGATCG'
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
        input_dict = final_config["input"]
        if isinstance(input_dict, dict):
            input_dict["sequence"] = sequence

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
        
    Example:
        >>> from primerlab.api import check_offtargets
        >>> result = check_offtargets(
        ...     forward_primer="ATGCGATCGATCGATCG",
        ...     reverse_primer="GCTAGCTAGCTAGCTAG",
        ...     database="human_genome.fasta"
        ... )
        >>> print(result["grade"])
        'A'
        >>> print(result["is_specific"])
        True
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
        
    Example:
        >>> from primerlab.api import check_primer_compatibility
        >>> primers = [
        ...     {"name": "Gene1", "fwd": "ATGCGATCGATCG", "rev": "GCTAGCTAGCTAG"},
        ...     {"name": "Gene2", "fwd": "CGATCGATCGATC", "rev": "TAGCTAGCTAGCT"}
        ... ]
        >>> result = check_primer_compatibility(primers)
        >>> print(result["is_valid"])
        True
        >>> print(result["grade"])
        'A'
    """
    from primerlab.core.compat_check.models import MultiplexPair
    from primerlab.core.compat_check.dimer import DimerEngine
    from primerlab.core.compat_check.scoring import MultiplexScorer
    from primerlab.core.compat_check.validator import MultiplexValidator
    from primerlab.core.config_loader import load_and_merge_config

    # Load config
    full_config = load_and_merge_config("compat_check", cli_overrides=config)

    # Map input to MultiplexPair models
    mapped_primers: List[MultiplexPair] = []
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
        
    Example:
        >>> from primerlab.api import analyze_amplicon
        >>> result = analyze_amplicon(sequence="ATGCGATCGATCGATCG...")
        >>> print(result["grade"])
        'A'
        >>> print(result["quality_score"])
        92.5
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


# ===== Tm Gradient API (v0.4.3) =====

def simulate_tm_gradient_api(
    primers: list,
    min_temp: float = 50.0,
    max_temp: float = 72.0,
    step_size: float = 0.5,
    na_concentration: float = 50.0,
    primer_concentration: float = 0.25
) -> Dict[str, Any]:
    """
    Simulate Tm gradient for optimal annealing temperature prediction.
    
    Args:
        primers: List of primer dicts with 'name', 'forward', 'reverse' keys
        min_temp: Minimum temperature (°C)
        max_temp: Maximum temperature (°C)
        step_size: Temperature step (°C)
        na_concentration: Na+ concentration (mM)
        primer_concentration: Primer concentration (µM)
        
    Returns:
        Dictionary containing:
        - optimal: optimal annealing temperature
        - range_min/range_max: recommended temperature range
        - primers: per-primer Tm and sensitivity data
    """
    from primerlab.core.tm_gradient import (
        TmGradientConfig,
        simulate_tm_gradient,
        predict_optimal_annealing,
    )

    config = TmGradientConfig(
        min_temp=min_temp,
        max_temp=max_temp,
        step_size=step_size,
        na_concentration=na_concentration,
        primer_concentration=primer_concentration
    )

    # Run simulations
    results = []
    for primer in primers:
        name = primer.get("name", "Unknown")
        fwd = primer.get("forward", primer.get("sequence", ""))
        rev = primer.get("reverse", "")

        if fwd:
            result = simulate_tm_gradient(fwd, f"{name}_fwd", config=config)
            results.append(result.to_dict())

        if rev:
            result = simulate_tm_gradient(rev, f"{name}_rev", config=config)
            results.append(result.to_dict())

    # Calculate optimal
    optimal = predict_optimal_annealing(primers, config)

    return {
        "optimal": optimal["optimal"],
        "range_min": optimal["range_min"],
        "range_max": optimal["range_max"],
        "primers": results
    }


def batch_species_check_api(
    primer_files: list = None,
    primer_dir: str = None,
    target_name: str = "Target",
    target_template: str = "",
    offtarget_templates: Optional[Dict[str, str]] = None,
    max_workers: int = 4,
    config: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Run batch species-check on multiple primer files.
    
    Args:
        primer_files: List of paths to primer JSON files
        primer_dir: Directory containing primer JSON files (alternative to primer_files)
        target_name: Name of target species
        target_template: Target species template sequence
        offtarget_templates: Dict mapping species names to sequences
        max_workers: Number of parallel threads
        config: Optional configuration
        
    Returns:
        Dictionary containing:
        - total_files: number of files processed
        - passed/failed: counts
        - pass_rate: percentage
        - results: per-file results
    """
    from primerlab.core.species import SpeciesTemplate
    from primerlab.core.species.batch import (
        load_primers_from_directory,
        load_primer_files,
        run_parallel_species_check,
    )
    from primerlab.core.species.batch.batch_loader import load_primer_files

    # Load primers
    if primer_dir:
        batch_input = load_primers_from_directory(primer_dir)
    elif primer_files:
        batch_input = load_primer_files(primer_files)
    else:
        raise ValueError("Must provide either primer_files or primer_dir")

    # Create templates
    target = SpeciesTemplate(species_name=target_name, sequence=target_template)

    offtargets = {}
    if offtarget_templates:
        for name, seq in offtarget_templates.items():
            offtargets[name] = SpeciesTemplate(species_name=name, sequence=seq)

    # Run parallel check
    result = run_parallel_species_check(
        batch_input=batch_input,
        target_template=target,
        offtarget_templates=offtargets,
        config=config,
        max_workers=max_workers
    )

    return result.to_dict()


# ===== qPCR Probe Binding API (v0.5.0) =====

def simulate_probe_binding_api(
    probe_sequence: str,
    amplicon_sequence: Optional[str] = None,
    min_temp: float = 55.0,
    max_temp: float = 72.0,
    step_size: float = 0.5,
    na_concentration: float = 50.0,
    probe_concentration: float = 0.25,
) -> Dict:
    """
    Simulate TaqMan probe binding for qPCR.
    
    Args:
        probe_sequence: Probe sequence (5' to 3')
        amplicon_sequence: Optional amplicon for position analysis
        min_temp: Minimum temperature (°C)
        max_temp: Maximum temperature (°C)
        step_size: Temperature step (°C)
        na_concentration: Na+ concentration (mM)
        probe_concentration: Probe concentration (μM)
        
    Returns:
        Dict with:
        - probe_tm: Calculated Tm
        - binding_efficiency: Peak efficiency
        - optimal_temp: Optimal annealing temperature
        - binding_curve: Efficiency at each temperature
        - position: Position analysis (if amplicon provided)
        - warnings: List of warnings
        - grade: A-F grade
    """
    from primerlab.core.qpcr.probe_binding import simulate_probe_binding
    from primerlab.core.qpcr.probe_position import analyze_probe_position

    # Run binding simulation
    result = simulate_probe_binding(
        probe_sequence=probe_sequence,
        min_temp=min_temp,
        max_temp=max_temp,
        step_size=step_size,
        na_concentration=na_concentration,
        probe_concentration=probe_concentration,
    )

    output = result.to_dict()

    # Add position analysis if amplicon provided
    if amplicon_sequence:
        position_result = analyze_probe_position(
            probe_sequence=probe_sequence,
            amplicon_sequence=amplicon_sequence,
        )
        output["position"] = position_result.to_dict()

    return output


def predict_melt_curve_api(
    amplicon_sequence: str,
    na_concentration: float = 50.0,
    min_temp: float = 65.0,
    max_temp: float = 95.0,
    step: float = 0.2,
) -> Dict:
    """
    Predict SYBR Green melt curve for an amplicon (v0.5.0).
    
    Args:
        amplicon_sequence: Amplicon DNA sequence
        na_concentration: Na+ concentration (mM)
        min_temp: Minimum temperature (°C)
        max_temp: Maximum temperature (°C)
        step: Temperature step (°C)
        
    Returns:
        Dict with:
        - predicted_tm: Melting temperature
        - tm_range: (min, max) expected Tm
        - peaks: List of detected peaks
        - melt_curve: Temperature vs -dF/dT data
        - is_single_peak: Boolean
        - quality_score: 0-100 score
        - grade: A-F grade
        - warnings: List of warnings
    """
    from primerlab.core.qpcr.melt_curve import predict_melt_curve

    result = predict_melt_curve(
        amplicon_sequence=amplicon_sequence,
        na_concentration=na_concentration,
        min_temp=min_temp,
        max_temp=max_temp,
        step=step,
    )

    return result.to_dict()


def validate_qpcr_amplicon_api(
    amplicon_sequence: str,
    min_length: int = 70,
    max_length: int = 150,
    gc_min: float = 40.0,
    gc_max: float = 60.0,
) -> Dict:
    """
    Validate amplicon for qPCR suitability (v0.5.0).
    
    Args:
        amplicon_sequence: Amplicon DNA sequence
        min_length: Minimum acceptable length (bp)
        max_length: Maximum acceptable length (bp)
        gc_min: Minimum GC percentage
        gc_max: Maximum GC percentage
        
    Returns:
        Dict with:
        - amplicon_length: Sequence length
        - gc_content: GC percentage
        - gc_ok: Boolean
        - length_ok: Boolean  
        - secondary_structure_ok: Boolean
        - tm_amplicon: Predicted Tm
        - quality_score: 0-100 score
        - grade: A-F grade
        - warnings: List of issues
        - recommendations: List of suggestions
    """
    from primerlab.core.qpcr.amplicon_qc import validate_qpcr_amplicon

    result = validate_qpcr_amplicon(
        amplicon_sequence=amplicon_sequence,
        min_length=min_length,
        max_length=max_length,
        gc_min=gc_min,
        gc_max=gc_max,
    )

    return result.to_dict()


def score_genotyping_primer_api(
    primer_sequence: str,
    snp_position: int,
    ref_allele: str,
    alt_allele: str,
    na_concentration: float = 50.0,
) -> Dict:
    """
    Score primer for SNP genotyping (allele-specific PCR) (v0.6.0).
    
    Args:
        primer_sequence: Primer sequence (5'→3')
        snp_position: Position of SNP from 3' end (0 = terminal)
        ref_allele: Reference allele
        alt_allele: Alternative allele
        na_concentration: Na+ concentration (mM)
        
    Returns:
        Dict with:
        - position_score: Score based on SNP position
        - mismatch_score: Score based on mismatch type
        - combined_score: Overall discrimination score
        - grade: A-F grade
        - is_discriminating: Boolean
        - tm_matched: Tm with matched allele
        - tm_mismatched: Tm with mismatched allele
        - delta_tm: Tm difference
        - specificity: Discrimination quality
        - warnings: List of warnings
        - recommendations: List of suggestions
    """
    from primerlab.core.genotyping.allele_scoring import score_allele_discrimination
    from primerlab.core.genotyping.snp_position import analyze_snp_context
    from primerlab.core.genotyping.discrimination_tm import (
        calculate_discrimination_tm,
        estimate_allele_specificity,
    )

    # Score allele discrimination
    scoring_result = score_allele_discrimination(
        primer_sequence=primer_sequence,
        snp_position=snp_position,
        ref_allele=ref_allele,
        alt_allele=alt_allele,
    )

    # Analyze SNP position
    primer_len = len(primer_sequence)
    snp_index = primer_len - 1 - snp_position  # Convert from 3' to 5' index
    position_result = analyze_snp_context(primer_sequence, snp_index)

    # Calculate Tm discrimination
    tm_matched, tm_mismatched, delta_tm = calculate_discrimination_tm(
        primer_sequence=primer_sequence,
        snp_position=snp_index,
        ref_allele=ref_allele,
        alt_allele=alt_allele,
        na_concentration=na_concentration,
    )

    # Estimate specificity
    specificity = estimate_allele_specificity(delta_tm)

    # Combine results
    output = scoring_result.to_dict()
    output["tm_matched"] = tm_matched
    output["tm_mismatched"] = tm_mismatched
    output["delta_tm"] = delta_tm
    output["specificity"] = specificity["specificity"]
    output["specificity_score"] = specificity["score"]
    output["snp_context"] = position_result.to_dict()

    # Merge recommendations
    output["recommendations"].extend(specificity["recommendations"])

    return output


def validate_rtpcr_primers_api(
    fwd_sequence: str,
    fwd_start: int,
    rev_sequence: str,
    rev_start: int,
    exon_boundaries: List[Tuple[int, int]],
    genomic_intron_sizes: Optional[List[int]] = None,
) -> Dict:
    """
    Validate RT-qPCR primers for exon-spanning and gDNA risk (v0.6.0).
    
    Args:
        fwd_sequence: Forward primer sequence
        fwd_start: Forward primer start position (transcript coordinates)
        rev_sequence: Reverse primer sequence
        rev_start: Reverse primer start position
        exon_boundaries: List of (start, end) for each exon
        genomic_intron_sizes: Optional list of intron sizes
        
    Returns:
        Dict with:
        - fwd_junction: Forward primer junction analysis
        - rev_junction: Reverse primer junction analysis
        - gdna_risk: gDNA contamination risk assessment
        - is_rt_specific: Boolean indicating RT-specificity
        - grade: Overall grade (A-F)
        - recommendations: List of suggestions
    """
    from primerlab.core.rtpcr.exon_junction import detect_exon_junction
    from primerlab.core.rtpcr.gdna_check import check_gdna_risk

    fwd_len = len(fwd_sequence)
    rev_len = len(rev_sequence)

    # Analyze forward primer junction
    fwd_junction = detect_exon_junction(
        primer_sequence=fwd_sequence,
        primer_start=fwd_start,
        exon_boundaries=exon_boundaries,
    )

    # Analyze reverse primer junction
    rev_junction = detect_exon_junction(
        primer_sequence=rev_sequence,
        primer_start=rev_start,
        exon_boundaries=exon_boundaries,
    )

    # Check gDNA risk
    gdna_risk = check_gdna_risk(
        fwd_start=fwd_start,
        fwd_end=fwd_start + fwd_len,
        rev_start=rev_start,
        rev_end=rev_start + rev_len,
        exon_boundaries=exon_boundaries,
        genomic_intron_sizes=genomic_intron_sizes,
    )

    # Calculate overall grade
    is_rt_specific = gdna_risk.is_rt_specific

    if fwd_junction.spans_junction or rev_junction.spans_junction:
        grade = "A"
    elif gdna_risk.risk_level == "Low":
        grade = "B"
    elif gdna_risk.risk_level == "Medium":
        grade = "C"
    else:
        grade = "F"

    # Combine recommendations
    recommendations = []
    recommendations.extend(fwd_junction.warnings)
    recommendations.extend(rev_junction.warnings)
    recommendations.extend(gdna_risk.recommendations)

    return {
        "fwd_junction": fwd_junction.to_dict(),
        "rev_junction": rev_junction.to_dict(),
        "gdna_risk": gdna_risk.to_dict(),
        "is_rt_specific": is_rt_specific,
        "grade": grade,
        "recommendations": recommendations,
    }
