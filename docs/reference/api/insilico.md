---
title: "In-silico PCR API"
description: "Python API reference for In-silico PCR API"
---
Virtual PCR simulation and primer binding analysis.

## Module

```python
from primerlab.core.insilico import (
    run_insilico_pcr,
    InsilicoPCR,
    analyze_binding,
    calculate_corrected_tm,
    check_three_prime_stability
)
```

---

## run_insilico_pcr()

Run virtual PCR simulation.

### Signature

```python
def run_insilico_pcr(
    forward: str,
    reverse: str,
    template_path: Path = None,
    template_seq: str = None,
    max_mismatches: int = 2,
    min_3prime_match: int = 3,
    circular: bool = False
) -> InsilicoPCRResult
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `forward` | str | required | Forward primer sequence (5'→3') |
| `reverse` | str | required | Reverse primer sequence (5'→3') |
| `template_path` | Path | None | Path to template FASTA |
| `template_seq` | str | None | Template sequence string |
| `max_mismatches` | int | 2 | Max mismatches allowed |
| `min_3prime_match` | int | 3 | Min perfect 3' match |
| `circular` | bool | False | Treat template as circular |

### Returns

`InsilicoPCRResult`:

- `products`: List of predicted amplicons
- `forward_binding`: Binding site analysis
- `reverse_binding`: Binding site analysis
- `is_specific`: True if single product

### Example: Basic Validation

```python
from primerlab.core.insilico import run_insilico_pcr

result = run_insilico_pcr(
    forward="ATGGTGAGCAAGGGCGAGGAG",
    reverse="TTACTTGTACAGCTCGTCCATGCC",
    template_path="gfp.fasta"
)

print(f"Products found: {len(result.products)}")
if result.is_specific:
    product = result.products[0]
    print(f"Amplicon size: {product.size} bp")
    print(f"Position: {product.start} - {product.end}")
```

### Example: With Template String

```python
template = "ATGGTGAGCAAGGGCGAGGAGCTGTTCACCGGG..."

result = run_insilico_pcr(
    forward="ATGGTGAGCAAGGGCGAGGAG",
    reverse="CCCGGTGAACAGCTCCTCGCC",  # reverse complement
    template_seq=template
)

for product in result.products:
    print(f"Size: {product.size} bp, Likelihood: {product.likelihood}%")
```

---

## analyze_binding()

Analyze primer binding at a specific site.

### Signature

```python
def analyze_binding(
    primer_seq: str,
    target_seq: str,
    position: int = 0
) -> BindingSite
```

### Returns

`BindingSite`:

- `position`: Binding position on template
- `mismatches`: Number of mismatches
- `mismatch_positions`: List of mismatch locations
- `three_prime_dg`: 3' end stability (ΔG)
- `estimated_tm`: Corrected Tm based on mismatches
- `validation_notes`: Warnings if any

### Example

```python
from primerlab.core.insilico import analyze_binding

binding = analyze_binding(
    primer_seq="ATGGTGAGCAAGGGCGAGGAG",
    target_seq="ATGGTGAGCAAGGGCGAGGAG"  # Perfect match
)

print(f"Mismatches: {binding.mismatches}")
print(f"3' ΔG: {binding.three_prime_dg:.2f} kcal/mol")
print(f"Estimated Tm: {binding.estimated_tm:.1f}°C")
```

---

## calculate_corrected_tm() (v0.3.4)

Calculate Tm corrected for mismatches.

### Signature

```python
def calculate_corrected_tm(
    primer_seq: str,
    target_seq: str,
    base_tm: float,
    mismatches: int,
    correction_per_mismatch: float = 2.5
) -> float
```

### Example

```python
from primerlab.core.insilico import calculate_corrected_tm

# Base Tm 60°C with 2 mismatches
corrected_tm = calculate_corrected_tm(
    primer_seq="ATGGTGAGCAAGGGCGAGGAG",
    target_seq="ATGGTGAGCAAGGGTGAGGAG",  # 1 mismatch
    base_tm=60.0,
    mismatches=1
)
print(f"Corrected Tm: {corrected_tm}°C")  # ~57.5°C
```

---

## check_three_prime_stability() (v0.3.4)

Check 3' end stability and generate warnings.

### Signature

```python
def check_three_prime_stability(
    three_prime_dg: float,
    threshold_strong: float = -9.0,
    threshold_weak: float = -3.0
) -> Optional[str]
```

### Returns

- `None` if 3' stability is OK
- Warning string if too stable or too weak

### Example

```python
from primerlab.core.insilico import check_three_prime_stability

warning = check_three_prime_stability(three_prime_dg=-10.5)
if warning:
    print(f"Warning: {warning}")
# Output: "Warning: 3' end too stable (ΔG=-10.5), may cause mispriming"
```

---

## See Also

- [Public API](public)
- [Models Reference](models)
