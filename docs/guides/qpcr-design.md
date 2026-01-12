# qPCR Assay Design Guide

Design TaqMan or SYBR Green quantitative PCR assays.

## Overview

PrimerLab supports two qPCR chemistries:

- **TaqMan** — Primers + hydrolysis probe (FAM/TAMRA)
- **SYBR Green** — Primers only (melt curve validation)

---

## TaqMan Assay Design

### Configuration

```yaml
input:
  sequence_path: ./target_gene.fasta

parameters:
  # Primer Tm
  tm:
    opt: 60.0
  
  # Probe Tm (5-10°C higher than primers)
  probe:
    tm:
      min: 65.0
      opt: 68.0
      max: 72.0
    size:
      min: 20
      max: 30
  
  # Short amplicon for qPCR
  product_size:
    min: 70
    max: 150

output:
  format: json
```

### Run Design

```bash
primerlab run qpcr --config taqman_config.yaml
```

### Output

```
🧬 PrimerLab qPCR Design (TaqMan)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 3 assays designed

Assay 1 (Score: 94.2)
  Forward: ATGGTGAGCAAGGGCGAG (Tm: 60.1°C)
  Reverse: CTTGTAGTTGCCGTCGTCC (Tm: 60.3°C)
  Probe:   CGAGCTGAAGGGCATCGACTTCAAG (Tm: 68.5°C)
  Amplicon: 95 bp
```

---

## SYBR Green Design

For SYBR Green, exclude probe configuration:

```yaml
input:
  sequence_path: ./target.fasta

parameters:
  tm:
    opt: 60.0
  product_size:
    min: 80
    max: 120
```

### Melt Curve Prediction

Validate SYBR assay with melt curve analysis:

```bash
primerlab melt-curve --amplicon output/amplicon.fasta --output melt.svg
```

This predicts the melt curve to ensure a single, specific product.

---

## qPCR Design Tips

### Amplicon Size

- **Optimal:** 70-150 bp for highest efficiency
- **Maximum:** 200 bp (efficiency drops above this)

### Probe Placement

- Position probe close to forward primer (within 10 bp)
- Avoid G at 5' end (quenches fluorophore)
- G+C content: 30-80%

### Avoid

- Runs of identical nucleotides (especially G)
- Secondary structures in amplicon
- SNPs under probe binding site

---

## Probe Validation

### Check Probe Binding

```bash
primerlab probe-check \
  --probe output/probe.json \
  --template target.fasta
```

### Check Assay Compatibility

```bash
primerlab check-compat \
  -p output/primers.json \
  --probe output/probe.json
```

This checks for primer-probe interactions that could reduce efficiency.

---

## RT-qPCR (cDNA)

For gene expression studies, design primers that span exon junctions:

```yaml
parameters:
  # Enable exon junction spanning
  exon_junction:
    enabled: true
    gtf_path: ./annotations.gtf
```

This prevents amplification of genomic DNA contamination.

---

## Complete Example

```bash
# Create config
cat > il6_qpcr.yaml << 'EOF'
input:
  sequence_path: ./IL6_transcript.fasta

parameters:
  tm:
    opt: 60.0
  probe:
    tm:
      opt: 68.0
  product_size:
    min: 80
    max: 120
EOF

# Design assay
primerlab run qpcr --config il6_qpcr.yaml --report

# Validate probe
primerlab probe-check \
  -p primerlab_output/probe.json \
  -t IL6_transcript.fasta

# Predict melt curve (for SYBR validation)
primerlab melt-curve \
  --amplicon primerlab_output/amplicon.fasta \
  --output IL6_melt.svg
```

---

## See Also

- [PCR Design](pcr-design) — Standard PCR primers
- [Nested PCR](nested-pcr) — Species specificity check
- [Configuration Reference](../reference/config) — All parameters
