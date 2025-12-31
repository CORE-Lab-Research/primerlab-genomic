# RT-qPCR Example

Example RT-qPCR primer validation for exon-spanning detection.

## Usage

```python
from primerlab.api import validate_rtpcr_primers_api

# Example: GAPDH-like transcript with 3 exons
exon_boundaries = [
    (0, 100),    # Exon 1
    (100, 250),  # Exon 2
    (250, 400),  # Exon 3
]

# Forward primer spans exon1-exon2 junction
result = validate_rtpcr_primers_api(
    fwd_sequence="ATGCGATCGATCGATCGATCG",
    fwd_start=90,   # 10bp in exon1, 11bp in exon2
    rev_sequence="ATGCGATCGATCGATCG",
    rev_start=180,
    exon_boundaries=exon_boundaries,
    genomic_intron_sizes=[5000, 3000],  # Intron sizes
)

print(f"RT-specific: {result['is_rt_specific']}")
print(f"Grade: {result['grade']}")
```

## Expected Output

```
RT-specific: True
Grade: A
```

## Quality Checklist

- [x] Forward primer spans junction
- [x] ≥5bp overlap on each side
- [x] No gDNA amplification risk
