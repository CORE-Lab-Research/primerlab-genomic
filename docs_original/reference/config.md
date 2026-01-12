---
title: "Configuration Reference"
description: "YAML configuration file reference for PrimerLab"
---

Complete reference for all PrimerLab configuration parameters.

---

## Configuration File Structure

```yaml
input:
  sequence: "ATCGATCG..."  # or sequence_path
  sequence_path: /path/to/sequence.fasta

parameters:
  tm:
    min: 57.0
    opt: 60.0
    max: 63.0
  
  primer_size:
    min: 18
    opt: 20
    max: 25
  
  product_size:
    min: 100
    max: 300
  
  gc:
    min: 40.0
    max: 60.0

output:
  format: json  # json, csv, text
  directory: ./output
```

---

## Parameter Reference

### Input Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `sequence` | string | Raw DNA sequence |
| `sequence_path` | path | Path to FASTA file |

### Tm (Melting Temperature)

| Parameter | Default | Range | Description |
|-----------|:-------:|:-----:|-------------|
| `tm.min` | 57.0 | 50-70 | Minimum Tm |
| `tm.opt` | 60.0 | 55-65 | Optimal Tm |
| `tm.max` | 63.0 | 58-72 | Maximum Tm |

### Primer Size

| Parameter | Default | Range | Description |
|-----------|:-------:|:-----:|-------------|
| `primer_size.min` | 18 | 15-25 | Minimum length |
| `primer_size.opt` | 20 | 18-22 | Optimal length |
| `primer_size.max` | 25 | 20-30 | Maximum length |

### Product Size

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `product_size.min` | 100 | Minimum amplicon |
| `product_size.max` | 300 | Maximum amplicon |

**Recommendations by workflow:**

| Workflow | Min | Max | Notes |
|----------|:---:|:---:|-------|
| Standard PCR | 200 | 1000 | Flexible |
| qPCR | 70 | 150 | Short preferred |
| Long-range PCR | 1000 | 10000 | Specialized enzymes |

### GC Content

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `gc.min` | 40.0 | Minimum GC% |
| `gc.max` | 60.0 | Maximum GC% |

---

## qPCR-Specific Parameters

```yaml
parameters:
  probe:
    tm:
      min: 65.0
      opt: 68.0
      max: 72.0
    size:
      min: 20
      max: 30
```

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `probe.tm.opt` | 68.0 | Probe Tm (5-10°C > primers) |
| `probe.size.min` | 20 | Minimum probe length |
| `probe.size.max` | 30 | Maximum probe length |

---

## Advanced Parameters

### Salt Concentrations

```yaml
parameters:
  salt:
    monovalent: 50.0   # mM (Na+, K+)
    divalent: 1.5      # mM (Mg2+)
    dntp: 0.2          # mM
```

### Thermodynamic Thresholds

```yaml
parameters:
  thermo:
    hairpin_dg_max: -2.0    # kcal/mol
    homodimer_dg_max: -5.0  # kcal/mol
    heterodimer_dg_max: -5.0
```

---

## Output Configuration

```yaml
output:
  format: json       # json, csv, text, html
  directory: ./output
  include_audit: true
  include_rationale: true
```

---

## Example Configurations

### Standard PCR

```yaml
input:
  sequence_path: ./gene.fasta

parameters:
  tm:
    opt: 60.0
  product_size:
    min: 200
    max: 500
```

### qPCR with TaqMan Probe

```yaml
input:
  sequence_path: ./target.fasta

parameters:
  tm:
    opt: 60.0
  product_size:
    min: 70
    max: 150
  probe:
    tm:
      opt: 68.0
```

### Long-Range PCR

```yaml
input:
  sequence_path: ./region.fasta

parameters:
  tm:
    opt: 65.0
  product_size:
    min: 2000
    max: 10000
  primer_size:
    opt: 25
```

---

## See Also

- [Getting Started](../getting-started)
- [CLI Reference](cli)
- [Examples](https://github.com/engkinandatama/primerlab-genomic/tree/main/examples)
