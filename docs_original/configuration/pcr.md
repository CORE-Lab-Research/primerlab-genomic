# PCR Configuration

Full reference for PCR primer design configuration.

## Minimal Config

```yaml
workflow: pcr

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output_pcr"
```

## Full Config

```yaml
workflow: pcr

# Optional: Use a preset (see presets.md)
# preset: long_range

input:
  # Inline sequence
  sequence: "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT..."
  # OR file path
  # sequence_path: "input.fasta"

parameters:
  # Primer size constraints
  primer_size:
    min: 18
    opt: 20
    max: 24

  # Melting temperature
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0

  # Product/amplicon size
  product_size_range: [[200, 600]]
  # For multiple ranges: [[100, 300], [400, 800]]

  # GC content
  gc:
    min: 40
    max: 60

  # Optional: Primer naming
  primer_naming:
    prefix: "GAPDH"
    forward_suffix: "_F"
    reverse_suffix: "_R"

output:
  directory: "output_pcr"
  formats:
    - json
    - markdown

qc:
  mode: standard  # standard, strict, relaxed
  hairpin_dg_max: -2.0
  homodimer_dg_max: -5.0
  heterodimer_dg_max: -5.0
  tm_diff_max: 3.0

advanced:
  timeout_seconds: 60
  debug: false
```

## Parameter Details

### primer_size

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| min | int | 18 | Minimum primer length |
| opt | int | 20 | Optimal primer length |
| max | int | 24 | Maximum primer length |

### tm

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| min | float | 58.0 | Minimum melting temperature |
| opt | float | 60.0 | Optimal melting temperature |
| max | float | 62.0 | Maximum melting temperature |

### product_size_range

List of [min, max] ranges for acceptable amplicon sizes.

```yaml
# Single range
product_size_range: [[200, 600]]

# Multiple ranges
product_size_range: [[100, 300], [400, 800]]
```

### gc

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| min | int | 40 | Minimum GC percentage |
| max | int | 60 | Maximum GC percentage |
