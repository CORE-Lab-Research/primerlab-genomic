# Public API

Main entry points for programmatic primer design.

## Module

```python
from primerlab.api import design_pcr_primers, design_qpcr_assays
```

---

## design_pcr_primers()

Design PCR primers for a DNA sequence.

### Signature

```python
def design_pcr_primers(
    sequence: str = None,
    sequence_path: Path = None,
    tm_range: tuple = (58, 62),
    product_size: tuple = (200, 600),
    gc_range: tuple = (40, 60),
    primer_size: tuple = (18, 20, 24),  # min, opt, max
    output_dir: str = "output",
    config_path: Path = None,
    qc_mode: str = "standard"
) -> WorkflowResult
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sequence` | str | None | DNA sequence (A/T/C/G). Either this or `sequence_path` required |
| `sequence_path` | Path | None | Path to FASTA file |
| `tm_range` | tuple | (58, 62) | (min, max) melting temperature °C |
| `product_size` | tuple | (200, 600) | (min, max) amplicon size bp |
| `gc_range` | tuple | (40, 60) | (min, max) GC percentage |
| `primer_size` | tuple | (18, 20, 24) | (min, opt, max) primer length |
| `output_dir` | str | "output" | Output directory path |
| `config_path` | Path | None | Optional YAML config override |
| `qc_mode` | str | "standard" | QC stringency: relaxed/standard/strict |

### Returns

`WorkflowResult` containing:

- `primers`: List of designed primer pairs
- `scores`: QC scores for each pair
- `report_path`: Path to generated report
- `success`: Boolean indicating completion

### Example: Basic Usage

```python
from primerlab.api import design_pcr_primers

# Design primers for GFP sequence
result = design_pcr_primers(
    sequence="ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGGGTGGTGCCC...",
    tm_range=(58, 62),
    product_size=(200, 500),
    output_dir="gfp_primers/"
)

# Check result
if result.success:
    print(f"Designed {len(result.primers)} primer pairs")
    for pair in result.primers[:3]:
        print(f"  Fwd: {pair.forward.sequence}")
        print(f"  Rev: {pair.reverse.sequence}")
        print(f"  Amplicon: {pair.amplicon_size} bp")
```

### Example: From FASTA File

```python
from primerlab.api import design_pcr_primers
from pathlib import Path

result = design_pcr_primers(
    sequence_path=Path("my_gene.fasta"),
    tm_range=(60, 65),
    qc_mode="strict",
    output_dir="strict_output/"
)
```

### Example: Custom Config

```python
from primerlab.api import design_pcr_primers

result = design_pcr_primers(
    sequence="ATGAGTAAAGGAGAAGAACTTTTC...",
    config_path=Path("custom_config.yaml")  # Override defaults
)
```

---

## design_qpcr_assays()

Design qPCR primers and probes (TaqMan or SYBR).

### Signature

```python
def design_qpcr_assays(
    sequence: str = None,
    sequence_path: Path = None,
    mode: str = "taqman",  # or "sybr"
    tm_range: tuple = (58, 62),
    probe_tm_range: tuple = (68, 72),
    product_size: tuple = (70, 150),
    output_dir: str = "output",
    qc_mode: str = "strict"
) -> WorkflowResult
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | str | "taqman" | Assay type: "taqman" or "sybr" |
| `probe_tm_range` | tuple | (68, 72) | Probe Tm range (TaqMan only) |
| `product_size` | tuple | (70, 150) | Shorter amplicons for qPCR |

### Example: TaqMan Assay

```python
from primerlab.api import design_qpcr_assays

result = design_qpcr_assays(
    sequence="ATGGTGAGCAAGGGCGAGGAG...",
    mode="taqman",
    product_size=(80, 120),
    output_dir="qpcr_taqman/"
)

if result.success:
    assay = result.primers[0]
    print(f"Fwd: {assay.forward.sequence}")
    print(f"Rev: {assay.reverse.sequence}")
    print(f"Probe: {assay.probe.sequence}")
```

### Example: SYBR Green

```python
result = design_qpcr_assays(
    sequence_path=Path("target.fasta"),
    mode="sybr",  # No probe needed
    output_dir="qpcr_sybr/"
)
```

---

## check_primer_compatibility() (v0.4.0)

Check compatibility of multiple primer pairs for multiplexing.

### Signature

```python
def check_primer_compatibility(
    primers: list[Dict[str, str]],
    config: Optional[Dict[str, Any]] = None
) -> Dict
```

### Example

```python
from primerlab.api import check_primer_compatibility

primers = [
    {"name": "GAPDH", "fwd": "ATGGGGAAGGTGAAGGTCGG", "rev": "GGATCTCGCTCCTGGAAGATG"},
    {"name": "ACTB", "fwd": "CATGTACGTTGCTATCCAGGC", "rev": "CTCCTTAATGTCACGCACGAT"}
]

result = check_primer_compatibility(primers)
print(f"Compatibility: {result['overall_compatibility']}%")
```

---

## analyze_amplicon() (v0.4.1)

Analyze an amplicon sequence for quality metrics.

### Signature

```python
def analyze_amplicon(
    sequence: str,
    config: Optional[Dict[str, Any]] = None
) -> Dict
```

### Example

```python
from primerlab.api import analyze_amplicon

result = analyze_amplicon("ATGCGATCGATCGATCGATCG...")
print(f"GC%: {result['gc_content']}")
print(f"Tm: {result['amplicon_tm']}°C")
print(f"Grade: {result['grade']}")
```

---

## check_species_specificity_api() (v0.4.2)

Check primer specificity across multiple species.

### Signature

```python
def check_species_specificity_api(
    primers: list[Dict[str, str]],
    target_template: str,
    target_name: str = "target",
    offtarget_templates: Optional[Dict[str, str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict
```

### Example

```python
from primerlab.api import check_species_specificity_api

primers = [{"name": "Gene1", "forward": "ATGC...", "reverse": "GCTA..."}]

result = check_species_specificity_api(
    primers=primers,
    target_template=human_seq,
    target_name="Human",
    offtarget_templates={"Mouse": mouse_seq}
)

print(f"Specificity: {result['overall_score']} ({result['grade']})")
```

---

## simulate_tm_gradient_api() (v0.4.3)

Simulate temperature gradient for optimal annealing prediction.

### Signature

```python
def simulate_tm_gradient_api(
    primers: list,
    min_temp: float = 50.0,
    max_temp: float = 72.0,
    step_size: float = 0.5,
    na_concentration: float = 50.0,
    primer_concentration: float = 0.25
) -> Dict
```

### Example

```python
from primerlab.api import simulate_tm_gradient_api

primers = [{"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG"}]

result = simulate_tm_gradient_api(
    primers=primers,
    min_temp=50.0,
    max_temp=70.0
)

print(f"Optimal: {result['optimal']}°C")
print(f"Range: {result['range_min']} - {result['range_max']}°C")
```

---

## batch_species_check_api() (v0.4.3)

Run batch species-check on multiple primer files.

### Signature

```python
def batch_species_check_api(
    primer_files: list = None,
    primer_dir: str = None,
    target_name: str = "Target",
    target_template: str = "",
    offtarget_templates: Optional[Dict[str, str]] = None,
    max_workers: int = 4,
    config: Optional[Dict] = None
) -> Dict
```

### Example

```python
from primerlab.api import batch_species_check_api

result = batch_species_check_api(
    primer_dir="primers/",
    target_name="Human",
    target_template=human_seq,
    max_workers=4
)

print(f"Pass rate: {result['pass_rate']}%")
print(f"Processed: {result['processed']}/{result['total_files']}")
```

---

## simulate_probe_binding_api() (v0.5.0)

Simulate TaqMan probe binding for qPCR.

### Signature

```python
def simulate_probe_binding_api(
    probe_sequence: str,
    amplicon_sequence: Optional[str] = None,
    min_temp: float = 55.0,
    max_temp: float = 72.0,
    step_size: float = 0.5,
    na_concentration: float = 50.0,
    probe_concentration: float = 0.25,
) -> Dict
```

### Example

```python
from primerlab.api import simulate_probe_binding_api

result = simulate_probe_binding_api(
    probe_sequence="ATGCGATCGATCGATCGATCG",
)

print(f"Probe Tm: {result['probe_tm']}°C")
print(f"Optimal: {result['optimal_temp']}°C")
print(f"Grade: {result['grade']}")
```

---

## predict_melt_curve_api() (v0.5.0)

Predict SYBR Green melt curve for amplicons.

### Signature

```python
def predict_melt_curve_api(
    amplicon_sequence: str,
    na_concentration: float = 50.0,
    min_temp: float = 65.0,
    max_temp: float = 95.0,
    step: float = 0.2,
) -> Dict
```

### Example

```python
from primerlab.api import predict_melt_curve_api

result = predict_melt_curve_api("ATGC" * 25)

print(f"Predicted Tm: {result['predicted_tm']}°C")
print(f"Single peak: {result['is_single_peak']}")
```

---

## validate_qpcr_amplicon_api() (v0.5.0)

Validate amplicon for qPCR suitability.

### Signature

```python
def validate_qpcr_amplicon_api(
    amplicon_sequence: str,
    min_length: int = 70,
    max_length: int = 150,
    gc_min: float = 40.0,
    gc_max: float = 60.0,
) -> Dict
```

### Example

```python
from primerlab.api import validate_qpcr_amplicon_api

result = validate_qpcr_amplicon_api("ATGC" * 25)

print(f"Length OK: {result['length_ok']}")
print(f"GC OK: {result['gc_ok']}")
print(f"Grade: {result['grade']}")
```

---

## score_genotyping_primer_api() (v0.6.0)

Score primers for SNP genotyping / allele discrimination assays.

### Signature

```python
def score_genotyping_primer_api(
    primer_sequence: str,
    snp_position: int,
    ref_allele: str,
    alt_allele: str,
    na_concentration: float = 50.0,
) -> Dict
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `primer_sequence` | str | - | Primer sequence (5'→3') |
| `snp_position` | int | - | SNP position from 3' end (0 = terminal) |
| `ref_allele` | str | - | Reference allele (A/T/C/G) |
| `alt_allele` | str | - | Alternative allele (A/T/C/G) |
| `na_concentration` | float | 50.0 | Na+ concentration in mM |

### Returns

Dict containing:

- `combined_score`: Overall discrimination score (0-100)
- `grade`: Quality grade (A-F)
- `is_discriminating`: Boolean if score >= threshold
- `tm_matched`: Tm for matched allele
- `tm_mismatched`: Tm for mismatched allele
- `delta_tm`: Tm difference
- `specificity`: Estimated allele specificity
- `warnings`: List of warnings
- `recommendations`: List of recommendations

### Example

```python
from primerlab.api import score_genotyping_primer_api

result = score_genotyping_primer_api(
    primer_sequence="ATGCGATCGATCGATCGATCG",
    snp_position=0,  # Terminal position
    ref_allele="G",
    alt_allele="A",
)

print(f"Score: {result['combined_score']}")
print(f"Grade: {result['grade']}")
print(f"ΔTm: {result['delta_tm']:.1f}°C")
```

---

## validate_rtpcr_primers_api() (v0.6.0)

Validate RT-qPCR primers for exon junction spanning and gDNA risk.

### Signature

```python
def validate_rtpcr_primers_api(
    fwd_sequence: str,
    fwd_start: int,
    rev_sequence: str,
    rev_start: int,
    exon_boundaries: List[Tuple[int, int]],
    genomic_intron_sizes: List[int] = None,
    min_junction_overlap: int = 5,
) -> Dict
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fwd_sequence` | str | - | Forward primer sequence |
| `fwd_start` | int | - | Forward primer start position |
| `rev_sequence` | str | - | Reverse primer sequence |
| `rev_start` | int | - | Reverse primer start position |
| `exon_boundaries` | List[Tuple] | - | List of (start, end) exon coordinates |
| `genomic_intron_sizes` | List[int] | None | Intron sizes for gDNA risk |
| `min_junction_overlap` | int | 5 | Min bp overlap on each side of junction |

### Returns

Dict containing:

- `fwd_junction`: Forward primer junction analysis
- `rev_junction`: Reverse primer junction analysis
- `gdna_risk`: gDNA contamination risk assessment
- `is_rt_specific`: Boolean if primers are RT-specific
- `grade`: Quality grade (A-F)
- `warnings`: List of warnings
- `recommendations`: List of recommendations

### Example

```python
from primerlab.api import validate_rtpcr_primers_api

exons = [(0, 100), (100, 200), (200, 300)]

result = validate_rtpcr_primers_api(
    fwd_sequence="ATGCGATCGATCGATCGATCG",
    fwd_start=90,  # Spans exon1-exon2 junction
    rev_sequence="ATGCGATCGATCGATCG",
    rev_start=150,
    exon_boundaries=exons,
)

print(f"RT-specific: {result['is_rt_specific']}")
print(f"gDNA Risk: {result['gdna_risk']['risk_level']}")
```

## Error Handling

```python
from primerlab.api import design_pcr_primers
from primerlab.core.exceptions import PrimerLabException

try:
    result = design_pcr_primers(
        sequence="ATGC...",
        tm_range=(58, 62)
    )
except PrimerLabException as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
```

---

## See Also

- [In-silico API](insilico.md)
- [Report API](report.md)
- [Models Reference](models.md)
- [Batch Processing](../features/batch-processing.md)
