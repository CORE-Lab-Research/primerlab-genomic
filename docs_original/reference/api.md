---
title: "API Reference"
description: "Python API for programmatic access to PrimerLab"
---

Python API for programmatic access to PrimerLab.

## Installation

```bash
pip install primerlab-genomic
```

## Quick Start

```python
from primerlab import design_pcr_primers, design_qpcr_assay

# Design PCR primers
result = design_pcr_primers(
    sequence="ATGCGATCGATCG...",
    tm_opt=60.0,
    product_size_range=(100, 300)
)

# Access results
for primer_pair in result.primer_pairs:
    print(f"Forward: {primer_pair.forward.sequence}")
    print(f"Reverse: {primer_pair.reverse.sequence}")
    print(f"Product: {primer_pair.product_size} bp")
```

---

## Core Functions

### `design_pcr_primers()`

Design standard PCR primers.

```python
from primerlab import design_pcr_primers

result = design_pcr_primers(
    sequence: str,                    # DNA sequence or path to FASTA
    tm_opt: float = 60.0,            # Optimal Tm (°C)
    tm_range: tuple = (57.0, 63.0),  # (min, max) Tm
    primer_size: tuple = (18, 20, 25), # (min, opt, max)
    product_size_range: tuple = (100, 300),
    gc_range: tuple = (40.0, 60.0),  # GC content %
    num_primers: int = 5,            # Number of pairs to return
    mask_regions: list = None,       # Regions to exclude
    output_dir: str = None           # Output directory
)
```

**Returns:** `PCRResult` object

---

### `design_qpcr_assay()`

Design qPCR primers with TaqMan probe.

```python
from primerlab import design_qpcr_assay

result = design_qpcr_assay(
    sequence: str,
    probe_tm_opt: float = 68.0,      # Probe Tm (5-10°C > primers)
    probe_size_range: tuple = (20, 30),
    assay_type: str = "taqman",      # or "sybr"
    **kwargs                         # Same as design_pcr_primers
)
```

**Returns:** `QPCRResult` object

---

### `run_insilico_pcr()`

Validate primers against template.

```python
from primerlab import run_insilico_pcr

result = run_insilico_pcr(
    forward: str,          # Forward primer sequence
    reverse: str,          # Reverse primer sequence
    template: str,         # Template sequence or FASTA path
    circular: bool = False # Circular template (plasmid)
)

# Check results
if result.success:
    for product in result.products:
        print(f"Amplicon: {product.size} bp at position {product.start}-{product.end}")
```

---

### `check_offtargets()`

Check primer specificity with BLAST.

```python
from primerlab import check_offtargets

result = check_offtargets(
    forward: str,
    reverse: str,
    database: str,         # Path to FASTA or BLAST DB
    target_id: str = None  # Expected target sequence ID
)

print(f"Specificity score: {result.score} ({result.grade})")
print(f"Off-targets found: {result.offtarget_count}")
```

---

### `check_compatibility()`

Check primer pair for dimers and hairpins.

```python
from primerlab import check_compatibility

result = check_compatibility(
    forward: str,
    reverse: str,
    probe: str = None  # Optional TaqMan probe
)

print(f"Self-dimer ΔG: {result.forward_self_dimer_dg} kcal/mol")
print(f"Hetero-dimer ΔG: {result.hetero_dimer_dg} kcal/mol")
print(f"Compatible: {result.is_compatible}")
```

---

## Result Objects

### `PCRResult`

```python
result.primer_pairs      # List of PrimerPair objects
result.metrics           # Design metrics
result.warnings          # Any warnings generated
result.output_dir        # Path to output files
```

### `PrimerPair`

```python
pair.forward             # Primer object
pair.reverse             # Primer object
pair.product_size        # Amplicon size (bp)
pair.product_gc          # Amplicon GC%
pair.score               # Quality score (0-100)
```

### `Primer`

```python
primer.sequence          # 5' to 3' sequence
primer.tm                # Melting temperature (°C)
primer.gc                # GC content (%)
primer.length            # Length (bp)
primer.position          # Position on template
primer.self_dimer_dg     # Self-dimer ΔG (kcal/mol)
primer.hairpin_dg        # Hairpin ΔG (kcal/mol)
```

### `QPCRResult`

Extends `PCRResult` with:

```python
result.probe             # Probe object (for TaqMan)
result.efficiency_estimate  # Predicted efficiency
```

---

## Configuration from File

Load configuration from YAML:

```python
from primerlab import run_workflow_from_config

result = run_workflow_from_config(
    config_path="my_config.yaml",
    workflow="pcr"  # or "qpcr"
)
```

---

## Error Handling

```python
from primerlab import design_pcr_primers
from primerlab.exceptions import (
    ConfigurationError,
    SequenceError,
    DesignError,
    DependencyError
)

try:
    result = design_pcr_primers(sequence="ATGC...", tm_opt=60.0)
except ConfigurationError as e:
    print(f"Config error: {e.message} (code: {e.error_code})")
except SequenceError as e:
    print(f"Sequence error: {e.message}")
except DesignError as e:
    print(f"Design failed: {e.message}")
except DependencyError as e:
    print(f"Missing dependency: {e.message}")
```

---

## Batch Processing

```python
from primerlab import batch_design

results = batch_design(
    fasta_path="genes.fasta",
    config_path="shared_config.yaml",
    parallel=4,
    continue_on_error=True
)

for seq_id, result in results.items():
    if result.success:
        print(f"{seq_id}: {len(result.primer_pairs)} pairs found")
    else:
        print(f"{seq_id}: FAILED - {result.error}")
```

---

## Full Example

```python
from primerlab import (
    design_pcr_primers,
    run_insilico_pcr,
    check_offtargets,
    check_compatibility
)

# 1. Design primers
design = design_pcr_primers(
    sequence="path/to/gene.fasta",
    tm_opt=60.0,
    product_size_range=(150, 250)
)

# 2. Get best pair
best = design.primer_pairs[0]
fwd = best.forward.sequence
rev = best.reverse.sequence

# 3. Validate with in-silico PCR
insilico = run_insilico_pcr(
    forward=fwd,
    reverse=rev,
    template="path/to/gene.fasta"
)
print(f"In-silico: {len(insilico.products)} product(s)")

# 4. Check specificity
offtarget = check_offtargets(
    forward=fwd,
    reverse=rev,
    database="path/to/genome.fasta"
)
print(f"Specificity: {offtarget.grade}")

# 5. Check compatibility
compat = check_compatibility(forward=fwd, reverse=rev)
print(f"Compatible: {compat.is_compatible}")
```

---

## See Also

- [CLI Reference](cli)
- [Configuration](config)
- [Getting Started](../getting-started)
