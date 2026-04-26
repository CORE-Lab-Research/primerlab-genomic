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

### GC Content

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `gc.min` | 40.0 | Minimum GC% |
| `gc.opt` | 50.0 | Optimal GC% (v0.8.0) |
| `gc.max` | 60.0 | Maximum GC% |

### Sequence Composition & Filtering (v0.8.0)

| Parameter | Default | Description |
|-----------|:-------:|-------------|
| `max_poly_x` | 4 | Maximum allowed mononucleotide repeat length |
| `max_ns` | 0 | Maximum allowed Ns in primer |
| `max_tm_diff` | 5.0 | Maximum Tm difference between forward and reverse primers |
| `num_candidates` | 50 | Number of primer pairs to generate |
| `included_region` | None | Dict with `start` and `length` to restrict design |
| `force_left_start`/`end` | None | Force forward primer coordinates |
| `force_right_start`/`end` | None | Force reverse primer coordinates |
| `must_match_five_prime` | None | 5' end constraint pattern |
| `must_match_three_prime` | None | 3' end constraint pattern |

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

### Thermodynamics and Salt Concentrations

PrimerLab natively uses Primer3's ThermoAnalysis engine to calculate precise melting temperatures and thermodynamic penalties.

```yaml
parameters:
  thermodynamics:
    salt_monovalent: 50.0      # mM (Na+, K+), default: 50.0
    salt_divalent: 1.5         # mM (Mg2+), default: 1.5
    dntp_conc: 0.6             # mM, default: 0.6
    dna_conc: 50.0             # nM, default: 50.0
    tm_method: santalucia      # santalucia or breslauer, default: santalucia
    salt_corrections: santalucia # santalucia, schildkraut, or owczarzy, default: santalucia
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `salt_monovalent` | float | 50.0 | Concentration of monovalent cations (mM) |
| `salt_divalent` | float | 1.5 | Concentration of divalent cations like Mg²⁺ (mM) |
| `dntp_conc` | float | 0.6 | Concentration of dNTPs (mM) |
| `dna_conc` | float | 50.0 | Concentration of oligos (nM) |
| `tm_method` | enum | santalucia | Nearest-neighbor parameter set (`santalucia` or `breslauer`) |
| `salt_corrections`| enum | santalucia | Salt correction formula (`santalucia`, `owczarzy`, or `schildkraut`) |

### Thermodynamic Thresholds

```yaml
parameters:
  thermo:
    hairpin_dg_max: -2.0    # kcal/mol
    homodimer_dg_max: -5.0  # kcal/mol
    heterodimer_dg_max: -5.0
```

### Advanced Primer3 Parameters (v0.8.0)

```yaml
parameters:
  qc_method: threshold # 'threshold' (using dG) or 'any' (using alignment scores)
  max_self_any_th: 47.0
  max_self_end_th: 47.0
  max_pair_compl_any_th: 47.0
  max_pair_compl_end_th: 47.0
  max_hairpin_th: 47.0
  
  weights:
    tm_gt: 1.0
    tm_lt: 1.0
    size_gt: 1.0
    size_lt: 1.0
    gc_percent_gt: 1.0
    gc_percent_lt: 1.0
    end_stability: 1.0
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

- [Getting Started](/docs/getting-started)
- [CLI Reference](cli)
- [Examples](https://github.com/engkinandatama/primerlab-genomic/tree/main/examples)
