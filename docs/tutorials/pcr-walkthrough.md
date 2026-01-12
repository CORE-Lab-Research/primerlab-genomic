---
title: "PCR Walkthrough"
description: "Tutorial: PCR Walkthrough"
---
Complete end-to-end PCR primer design workflow.

## Overview

This tutorial covers:

1. Sequence preparation
2. Configuration options
3. Running design
4. Interpreting results
5. Validation
6. Off-target check

---

## 1. Sequence Preparation

### Check your sequence first

```bash
primerlab stats my_gene.fasta
```

Output:

```
📊 Sequence Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name:     My_Target_Gene
Length:   600 bp
GC:       48.5%
Valid:    ✅ All bases valid
```

### Requirements

- Minimum 100 bp recommended
- FASTA format
- Valid DNA bases (A, T, C, G, or IUPAC codes)

---

## 2. Configuration Options

### Minimal config

```yaml
workflow: pcr

input:
  sequence_path: "my_gene.fasta"

output:
  directory: "output/"
```

### Full config with all options

```yaml
workflow: pcr

# Use a preset (optional)
# preset: long_range

input:
  sequence_path: "my_gene.fasta"

parameters:
  # Primer size
  primer_size:
    min: 18
    opt: 20
    max: 24
  
  # Melting temperature
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0
  
  # Product size (can specify multiple ranges)
  product_size_range: [[200, 400], [400, 600]]
  
  # GC content
  gc:
    min: 40
    max: 60

qc:
  mode: standard  # relaxed, standard, strict
  hairpin_dg_max: -2.0
  homodimer_dg_max: -5.0
  heterodimer_dg_max: -5.0

output:
  directory: "output_pcr"

advanced:
  num_candidates: 50
  debug: false
```

---

## 3. Running Design

### Basic run

```bash
primerlab run pcr --config my_config.yaml
```

### With validation

```bash
primerlab run pcr --config my_config.yaml --validate
```

### With off-target check

```bash
primerlab run pcr --config my_config.yaml --blast --blast-db /path/to/genome
```

### With report

```bash
primerlab run pcr --config my_config.yaml --report --report-format html
```

### All options combined

```bash
primerlab run pcr \
  --config my_config.yaml \
  --validate \
  --blast --blast-db /path/to/genome \
  --report --report-format html \
  --debug
```

---

## 4. Interpreting Results

### Output files

```
output_pcr/
├── result.json        # Machine-readable results
├── report.md          # Human-readable report
├── report.html        # HTML report (if --report-format html)
└── audit.json         # Reproducibility log
```

### Understanding scores

| Score | Grade | Meaning |
|-------|-------|---------|
| 90-100 | A | Excellent |
| 80-89 | B | Good |
| 70-79 | C | Acceptable |
| 60-69 | D | Poor |
| &lt;60 | F | Reject |

### Key metrics

| Metric | Ideal | Notes |
|--------|-------|-------|
| Tm difference | &lt;2°C | Primers should match |
| GC content | 40-60% | For stability |
| Hairpin ΔG | >-2 kcal/mol | Avoid stable hairpins |
| 3' stability | Moderate | Not too stable/weak |

---

## 5. Validation

### In-silico PCR

```bash
primerlab insilico \
  -f "ATGAGTAAAGGAGAAGAACT" \
  -r "GCCGTGATGTATACATTGTG" \
  -t my_gene.fasta
```

### Check binding

```bash
primerlab insilico \
  -p output_pcr/result.json \
  -t my_gene.fasta \
  --show-alignment
```

---

## 6. Off-target Check

### Setup BLAST database

```bash
makeblastdb -in genome.fasta -dbtype nucl -out genome_db
```

### Run check

```bash
primerlab blast \
  -p output_pcr/result.json \
  -d genome_db
```

### Interpret grades

| Grade | Off-targets | Recommendation |
|-------|-------------|----------------|
| A | 0 | ✅ Use |
| B | 1-2 (low identity) | ✅ Use |
| C | 3-5 | ⚠️ Verify |
| D | 6-10 | ⚠️ Consider alternatives |
| F | >10 | ❌ Do not use |

---

## Summary Workflow

```
1. primerlab stats input.fasta     # Check sequence
2. primerlab init --workflow pcr   # Create config template
3. # Edit config as needed
4. primerlab run pcr --config ...  # Design primers
5. primerlab insilico ...          # Validate
6. primerlab blast ...             # Off-target check
7. # Order primers!
```

---

## Next Steps

- [qPCR Design](qpcr-design)
- [Presets](../configuration/presets)
- [Troubleshooting](../troubleshooting)
