# qPCR Configuration

Full reference for qPCR primer and probe design configuration.

## Modes

| Mode | Description |
|------|-------------|
| `taqman` | Design primers + probe (default) |
| `sybr` | Design primers only (no probe) |

## Minimal Config (TaqMan)

```yaml
workflow: qpcr

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output_qpcr"
```

## Minimal Config (SYBR Green)

```yaml
workflow: qpcr

parameters:
  mode: sybr

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output_qpcr_sybr"
```

## Full Config (TaqMan)

```yaml
workflow: qpcr

input:
  sequence_path: "my_gene.fasta"

parameters:
  mode: taqman  # default
  
  # Primer parameters
  primer_size:
    min: 18
    opt: 20
    max: 24
  
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0
  
  # qPCR-specific: shorter amplicons
  product_size_range: [[70, 150]]
  
  gc:
    min: 40
    max: 60
  
  # Probe parameters
  probe:
    size:
      min: 18
      opt: 24
      max: 30
    tm:
      min: 68
      opt: 70
      max: 72

output:
  directory: "output_qpcr"

qc:
  mode: strict  # Recommended for qPCR
```

## Probe Parameters

TaqMan probes typically have:

- **Higher Tm** than primers (68-72°C)
- **Size** of 18-30 bp
- **No G at 5' end** (quenches fluorescence)

```yaml
probe:
  size:
    min: 18
    opt: 24
    max: 30
  tm:
    min: 68
    opt: 70
    max: 72
```

## Product Size

For qPCR, shorter amplicons (70-150 bp) are preferred for:

- Higher amplification efficiency
- Better quantification accuracy
- Compatibility with degraded samples

```yaml
product_size_range: [[70, 150]]
```
