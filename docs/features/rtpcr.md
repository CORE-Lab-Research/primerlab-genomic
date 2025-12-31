# RT-qPCR Primer Validation (v0.6.0)

Validate RT-qPCR primers for exon-spanning and gDNA contamination risk.

## Overview

The RT-qPCR module ensures primers are specific to mRNA:

- **Exon Junction Detection** - Primers spanning junctions won't amplify gDNA
- **gDNA Risk Assessment** - Evaluate contamination risk
- **Transcript Annotation** - Load exon boundaries from GTF/BED files

## Python API

### validate_rtpcr_primers_api

```python
from primerlab.api import validate_rtpcr_primers_api

# Define exon boundaries (transcript coordinates)
exon_boundaries = [
    (0, 100),    # Exon 1: 0-100bp
    (100, 200),  # Exon 2: 100-200bp
    (200, 300),  # Exon 3: 200-300bp
]

result = validate_rtpcr_primers_api(
    fwd_sequence="ATGCGATCGATCGATCGATCG",
    fwd_start=90,   # Spans exon1-exon2 junction
    rev_sequence="ATGCGATCGATCGATCG",
    rev_start=150,
    exon_boundaries=exon_boundaries,
)

print(f"RT-specific: {result['is_rt_specific']}")
print(f"Grade: {result['grade']}")
print(f"gDNA Risk: {result['gdna_risk']['risk_level']}")
```

## Exon Junction Spanning

For RT-specificity, primers should span exon-exon junctions:

| Position | RT-Specific | gDNA Amplifies |
|----------|-------------|----------------|
| Spans junction | ✅ Yes | ❌ No |
| Same exon | ❌ No | ✅ Yes |
| Large intron between | ✅ Likely | ⚠️ Unlikely |

## gDNA Risk Levels

| Risk Level | Meaning | Action |
|------------|---------|--------|
| None | Junction-spanning | ✅ Safe |
| Low | Large intron (>1kb) | ✅ Acceptable |
| Medium | Small intron | ⚠️ Consider DNase |
| High | Same exon | ❌ Redesign |

## Optimal Junction Overlap

For reliable RT-specificity, primers should have ≥5bp on each side of junction:

```
5' exon (≥5bp) | Junction | 3' exon (≥5bp)
     ATGCG     |    ||    |     ATCGA
```

## Use Cases

1. **Gene Expression (RT-qPCR)** - Ensure cDNA-specific amplification
2. **Transcript Variant Detection** - Target specific splice isoforms
3. **RNA Quality Assessment** - Verify no gDNA contamination

## See Also

- [qPCR Advanced Tutorial](../tutorials/qpcr-advanced.md)
- [Melt Curve Analysis](melt-curve.md)
