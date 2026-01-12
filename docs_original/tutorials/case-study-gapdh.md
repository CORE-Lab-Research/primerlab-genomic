---
title: "Case Study: Housekeeping Gene Primers"
description: "Design PCR primers for GAPDH reference gene normalization"
---

A practical tutorial for designing primers for reference gene normalization in qPCR experiments.

## Objective

Design **PCR primers** for the human **GAPDH** (Glyceraldehyde-3-phosphate dehydrogenase) gene, a commonly used housekeeping gene for RT-qPCR normalization.

**Requirements**:

- Amplicon size: 150-250 bp (optimal for qPCR)
- Tm: 58-62°C for standard cycling
- High specificity to avoid pseudogene amplification

---

## Step 1: Input Sequence

We'll use the GAPDH sequence from the project's example files.

```bash
# View the sequence
head -8 examples/multi_sequences.fasta
```

```fasta
>GAPDH_human Glyceraldehyde-3-phosphate dehydrogenase
ATGGTGAAGGTCGGAGTCAACGGATTTGGTCGTATTGGGCGCCTGGTCACCAGGGCTGCT
TTTAACTCTGGTAAAGTGGATATTGTTGCCATCAATGACCCCTTCATTGACCTCAACTAC
ATGGTTTACATGTTCCAATATGATTCCACCCATGGCAAATTCCATGGCACCGTCAAGGCT
GAGAACGGGAAGCTTGTCATCAATGGAAATCCCATCACCATCTTCCAGGAGCGAGATCCC
TCCAAAATCAAGTGGGGCGATGCTGGCGCTGAGTACGTCGTGGAGTCCACTGGCGTCTTC
ACCACCATGGAGAAGGCTGGGGCTCATTTGCAGGGGGGAGCCAAAAGGGTCATCATCTCT
```

---

## Step 2: Configuration

Create `gapdh_design.yaml`:

```yaml
workflow: pcr

input:
  sequence_path: ./examples/multi_sequences.fasta
  target_id: GAPDH_human  # Select specific sequence

parameters:
  # Primer settings
  primer_size:
    min: 18
    opt: 20
    max: 25
  
  # Melting temperature
  tm:
    min: 58.0
    opt: 60.0
    max: 62.0
  
  # Amplicon size - optimal for qPCR
  product_size_range: [[150, 250]]
  
  # GC content
  gc:
    min: 45.0
    max: 55.0

qc:
  mode: standard

output:
  directory: ./output_gapdh
  include_rationale: true
```

---

## Step 3: Run Design

```bash
primerlab run pcr --config gapdh_design.yaml
```

**Expected Output**:

```
🧬 PrimerLab PCR Design
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 5 primer pairs designed

Pair 1 (Score: 94)
  Forward: ATGGTGAAGGTCGGAGTCAAC (Tm: 60.1°C)
  Reverse: CCTGCAAATGAGCCCCAGCC (Tm: 60.3°C)
  Product: 198 bp
  Grade: Excellent ✅

📁 Output: ./output_gapdh/
```

---

## Step 4: Interpret Results

Open `./output_gapdh/primers.json` to see detailed results:

```json
{
  "rank": 1,
  "score": 94,
  "grade": "Excellent",
  "forward": {
    "sequence": "ATGGTGAAGGTCGGAGTCAAC",
    "tm": 60.1,
    "gc_percent": 52.4,
    "length": 21,
    "hairpin_dg": -1.2,
    "self_dimer_dg": -3.5
  },
  "reverse": {
    "sequence": "CCTGCAAATGAGCCCCAGCC",
    "tm": 60.3,
    "gc_percent": 60.0,
    "length": 20,
    "hairpin_dg": -0.8,
    "self_dimer_dg": -2.9
  },
  "product_size": 198,
  "penalties": {
    "primer3": -3,
    "gc_clamp_rev": -3
  }
}
```

### Understanding the Output

| Metric | Value | Interpretation |
|--------|:-----:|----------------|
| Score | 94 | Excellent (85-100 range) |
| Tm Difference | 0.2°C | Ideal (< 2°C) |
| Hairpin ΔG | -1.2, -0.8 | Safe (> -2 is good) |
| Self-dimer ΔG | -3.5, -2.9 | Safe (> -5 is good) |

---

## Step 5: Validate with In-Silico PCR

Verify the primers amplify correctly:

```bash
primerlab insilico \
  -p output_gapdh/primers.json \
  -t examples/multi_sequences.fasta \
  --target GAPDH_human
```

**Expected**:

```
✅ 1 product found
  Position: 1-198
  Size: 198 bp
  Match: GAPDH_human
```

---

## Step 6: Generate Order File

Export for synthesis ordering:

```bash
primerlab run pcr --config gapdh_design.yaml --export idt
```

This creates `output_gapdh/primers_idt.csv` ready for upload to IDT.

---

## Batch Design: All Housekeeping Genes

Design primers for all 10 genes at once:

```bash
primerlab run pcr \
  --fasta examples/multi_sequences.fasta \
  --batch \
  --out output_housekeeping/
```

This generates primers for GAPDH, ACTB, B2M, 18S, HPRT1, RPL13A, SDHA, TBP, YWHAZ, and PPIA.

---

## Summary

We successfully designed primers for GAPDH with:

- **Score**: 94/100 (Excellent)
- **Amplicon**: 198 bp (ideal for qPCR)
- **Tm Match**: 0.2°C difference (perfect)
- **No Warnings**: All QC checks passed

---

## See Also

- [PCR Design Guide](../guides/pcr-design)
- [Understanding Results](../concepts/understanding-results)
- [Batch Processing](../guides/batch-design)
