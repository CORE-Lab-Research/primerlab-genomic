---
title: "Advanced Configuration"
description: "In-depth guide to PrimerLab configuration options"
---

A deep dive into every possible configuration parameter in PrimerLab. Use this guide to fine-tune your designs.

## File Structure

The configuration file is a YAML document divided into 5 main sections:

1. `input`
2. `workflow`
3. `parameters`
4. `filtering`
5. `output`

---

## 1. Input (`input`)

Defines the source of your DNA sequence.

```yaml
input:
  # Path to local FASTA file (Recommended)
  sequence_path: "./data/gene.fasta"
  
  # OR direct sequence string (For short tests)
  sequence: "ATGC..."
  
  # For batch mode, this is ignored and CLI input is used
```

---

## 2. Workflow (`workflow`)

Selects the design engine.

```yaml
workflow: pcr   # Standard PCR
# OR
workflow: qpcr  # Quantitative PCR
```

---

## 3. Parameters (`parameters`)

The core design constraints.

### `tm` (Melting Temperature)

Uses nearest-neighbor thermodynamics (SantaLucia 1998).

```yaml
tm:
  min: 57.0  # Minimum allowed Tm
  opt: 60.0  # Target Tm (Score penalty moves away from here)
  max: 63.0  # Maximum allowed Tm
```

### `primer_size`

Length of the primer in base pairs.

```yaml
primer_size:
  min: 18
  opt: 20
  max: 25
```

### `product_size`

Length of the resulting amplicon.

```yaml
product_size:
  min: 100
  max: 300
```

> **Tip**: For qPCR, keep `max` below 150 bp for best efficiency.

### `gc` (GC Content)

Percentage of G and C bases.

```yaml
gc:
  min: 30.0
  max: 70.0
  clamp: 1   # Enforce at least 1 G/C at 3' end (0 to disable)
```

---

## 4. qPCR Specific (`probe`)

Only used if `workflow: qpcr`.

```yaml
probe:
  tm:
    min: 68.0
    opt: 70.0  # Should be ~10°C higher than primer Tm
    max: 72.0
  size:
    min: 18
    max: 30
  exclude_5_g: true  # Avoid G at 5' end (quenches fluorophore)
```

---

## 5. Filtering & Weights (`filtering`, `scoring`)

Advanced control over the ranking algorithm.

```yaml
filtering:
  max_poly_x: 5       # Reject runs of 5+ identical bases (e.g., AAAAA)
  max_self_dimer: -5.0 # Max delta G for self-dimer (kcal/mol)
  max_hairpin: -2.0    # Max delta G for hairpin

scoring:
  weights:
    tm: 1.0     # Importance of Tm accuracy
    gc: 0.5     # Importance of GC
    dimer: 2.0  # Importance of avoiding dimers (High!)
    size: 0.5   # Importance of exact product size
```
