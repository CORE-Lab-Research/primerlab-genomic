---
title: "Tutorial: Tm Gradient Simulation"
description: "Tutorial: Tutorial: Tm Gradient Simulation"
---
Learn how to use Tm gradient simulation to find optimal annealing temperatures.

## Prerequisites

- PrimerLab v0.4.3+
- Primer JSON file

## Step 1: Prepare Primers

Create `primers.json`:

```json
[
  {
    "name": "BRCA1_Ex10",
    "forward": "ATGCGATCGATCGATCGATCG",
    "reverse": "GCTAGCTAGCTAGCTAGCTAG"
  },
  {
    "name": "TP53_Ex5",
    "forward": "GCGCGCGCGCGCGCGCGCGC",
    "reverse": "ATATATATATATATATATATAT"
  }
]
```

## Step 2: Run Simulation

```bash
primerlab tm-gradient -p primers.json -o results/
```

## Step 3: Interpret Results

### Optimal Temperature

The **optimal annealing temperature** is where all primers have good binding efficiency while maintaining specificity.

### Recommended Range

The **recommended range** shows temperatures where efficiency stays above 80%.

### Per-Primer Analysis

```
Primer1_fwd: Tm=62.3°C, Optimal=57.3°C (Grade A)
              ↑           ↑              ↑
              |           |              +-- Overall grade
              |           +-- Best annealing temp (Tm - 5°C)
              +-- Calculated melting temperature
```

### Grades

| Grade | Score | Meaning |
|-------|-------|---------|
| A | ≥90 | Excellent - wide temperature tolerance |
| B | ≥80 | Good - stable across range |
| C | ≥70 | Acceptable - moderate sensitivity |
| D | ≥60 | Poor - narrow window |
| F | &lt;60 | Fail - redesign recommended |

## Step 4: Use in PCR Protocol

Based on results:

1. Set gradient PCR from `range_min` to `range_max`
2. Use `optimal` as starting point
3. Validate with actual amplification

## Advanced: Custom Temperature Range

For high-Tm primers (GC-rich):

```bash
primerlab tm-gradient -p primers.json --min-temp 55 --max-temp 75 --step 0.5
```

For low-Tm primers:

```bash
primerlab tm-gradient -p primers.json --min-temp 45 --max-temp 65 --step 0.5
```

## Python API Example

```python
from primerlab.api import simulate_tm_gradient_api

result = simulate_tm_gradient_api(
    primers=[{"name": "P1", "forward": "ATGCGATCGATCGATCGATCG"}],
    min_temp=50.0,
    max_temp=72.0
)

# Access efficiency curve for plotting
for primer in result["primers"]:
    print(f"{primer['primer_name']}: Tm={primer['calculated_tm']:.1f}°C")
    for dp in primer["data_points"][:5]:  # First 5 points
        print(f"  {dp['temperature']}°C: {dp['binding_efficiency']:.1f}%")
```

## Next Steps

- [Species Specificity Check](species-check)
- [Tm Gradient Feature Docs](../features/tm-gradient)
