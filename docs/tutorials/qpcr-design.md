---
title: "qPCR Design Tutorial"
description: "Tutorial: qPCR Design Tutorial"
---
Design TaqMan or SYBR Green assays.

## TaqMan vs SYBR Green

| Mode | Probe | Use Case |
|------|-------|----------|
| `taqman` | Yes | Specific detection, multiplexing |
| `sybr` | No | Cost-effective, simple |

---

## TaqMan Assay Design

### Configuration

```yaml
workflow: qpcr

input:
  sequence_path: "target_gene.fasta"

parameters:
  mode: taqman  # Default
  
  # Primer parameters
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  
  # qPCR requires short amplicons
  product_size_range: [[70, 150]]
  
  # Probe parameters
  probe:
    size: {min: 18, opt: 24, max: 30}
    tm: {min: 68, opt: 70, max: 72}

qc:
  mode: strict  # Recommended for qPCR

output:
  directory: "output_qpcr"
```

### Run

```bash
primerlab run qpcr --config qpcr_config.yaml
```

### Output

```json
{
  "forward": {
    "sequence": "ATGAGTAAAGGAGAAGAACT",
    "tm": 58.5
  },
  "reverse": {
    "sequence": "GCCGTGATGTATACATTGTG",
    "tm": 59.2
  },
  "probe": {
    "sequence": "TGTTGAATTAGATGGTGATGTTAA",
    "tm": 70.1
  },
  "amplicon_size": 95
}
```

---

## SYBR Green Design

### Configuration

```yaml
workflow: qpcr

input:
  sequence_path: "target_gene.fasta"

parameters:
  mode: sybr  # No probe
  product_size_range: [[80, 200]]

output:
  directory: "output_sybr"
```

### Run

```bash
primerlab run qpcr --config sybr_config.yaml
```

---

## Key Considerations

### Probe Design Rules

- Tm 8-10°C higher than primers
- No G at 5' end (quenches fluorescence)
- Avoid long G runs (>4)
- 18-30 bp length

### Amplicon Size

- 70-150 bp ideal for qPCR
- Short = higher efficiency
- Long = better sensitivity

---

## Validation

```bash
primerlab insilico \
  -f "ATGAGTAAAGGAGAAGAACT" \
  -r "GCCGTGATGTATACATTGTG" \
  -t target_gene.fasta
```

---

## Next Steps

- [Off-target Analysis](offtarget-tutorial)
- [PCR Walkthrough](pcr-walkthrough)
- [Troubleshooting](../troubleshooting)
