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
