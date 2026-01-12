---
title: "Genotyping / Allele Discrimination"
description: "Feature documentation: Genotyping / Allele Discrimination"
---
Score primers for SNP genotyping assays (allele-specific PCR).

## Overview

The genotyping module evaluates primer suitability for allele-specific PCR:

- **SNP Position** - 3' terminal = best discrimination
- **Mismatch Type** - Transversions discriminate better than transitions
- **Tm Difference** - Higher delta Tm = better specificity

## Python API

### score_genotyping_primer_api

```python
from primerlab.api import score_genotyping_primer_api

result = score_genotyping_primer_api(
    primer_sequence="ATGCGATCGATCGATCGA",
    snp_position=0,        # Distance from 3' end
    ref_allele="A",
    alt_allele="T",
)

print(f"Grade: {result['grade']}")
print(f"Delta Tm: {result['delta_tm']}°C")
print(f"Specificity: {result['specificity']}")
```

## SNP Position Guidelines

| Position from 3' | Weight | Discrimination |
|------------------|--------|----------------|
| 0 (terminal) | 1.0 | Best |
| 1 | 0.7 | Good |
| 2 | 0.4 | Acceptable |
| 3 | 0.2 | Marginal |
| 4+ | &lt;0.2 | Poor |

## Mismatch Type Scoring

Transversions (purine ↔ pyrimidine) provide better discrimination:

| Mismatch | Score | Type |
|----------|-------|------|
| A↔T | 1.0 | Transversion (best) |
| G↔T | 0.95 | Transversion |
| A↔C | 0.9 | Transversion |
| G↔C | 0.85 | Transversion |
| A↔G | 0.6 | Transition |
| C↔T | 0.6 | Transition |

## Tm Discrimination

| Delta Tm | Specificity | Score |
|----------|-------------|-------|
| ≥8°C | Excellent | 100 |
| ≥5°C | Good | 85 |
| ≥3°C | Moderate | 70 |
| ≥1.5°C | Marginal | 55 |
| &lt;1.5°C | Poor | 40 |

## Use Cases

1. **SNP Genotyping** - Detect known variants
2. **Mutation Screening** - Quick PCR-based detection
3. **Allele-Specific PCR (AS-PCR)** - Distinguish alleles

## See Also

- [Species Specificity](species-specificity)
- [Probe Binding](probe-binding)
