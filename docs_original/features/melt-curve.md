# SYBR Green Melt Curve Analysis (v0.5.0)

Predict melt curve characteristics for SYBR Green qPCR amplicons.

## Overview

The melt curve module predicts:

- **Amplicon Tm** - Melting temperature of the PCR product
- **Melt Profile** - -dF/dT curve shape
- **Peak Detection** - Single vs multiple peaks
- **Quality Score** - Assessment of amplicon suitability

## Why Melt Curve Analysis?

SYBR Green binds to all double-stranded DNA. Melt curve analysis helps:

1. **Confirm Specificity** - Single peak = single product
2. **Detect Primer-Dimers** - Lower Tm peaks
3. **Identify Non-Specific** - Multiple peaks

## Python API

### predict_melt_curve

```python
from primerlab.core.qpcr import predict_melt_curve

result = predict_melt_curve(
    amplicon_sequence="ATGC" * 25,  # 100bp
    na_concentration=50.0,
)

print(f"Predicted Tm: {result.predicted_tm}°C")
print(f"Single peak: {result.is_single_peak}")
print(f"Grade: {result.grade}")
```

### Report Generation

```python
from primerlab.core.qpcr import (
    predict_melt_curve,
    generate_melt_markdown,
    generate_melt_csv,
)

result = predict_melt_curve("ATGC" * 25)

# Markdown report
md = generate_melt_markdown(result)

# CSV data for plotting
csv = generate_melt_csv(result)
```

## Optimal Amplicon Properties

| Property | Optimal | Acceptable |
|----------|---------|------------|
| Length | 80-120 bp | 70-200 bp |
| GC% | 40-60% | 30-70% |
| Tm | 80-88°C | 75-92°C |

## Interpreting Results

### Single Peak (Grade A-B)

✅ Indicates specific amplification:

- One clean melt peak
- Sharp transition
- Consistent Tm between replicates

### Multiple Peaks (Review Required)

⚠️ May indicate:

- **Lower peak** - Primer-dimers
- **Higher peak** - Wrong target
- **Shoulder** - Non-specific products

## Output

### MeltCurveResult

```python
@dataclass
class MeltCurveResult:
    amplicon_sequence: str
    predicted_tm: float
    tm_range: Tuple[float, float]
    peaks: List[MeltPeak]
    melt_curve: List[Dict]  # {temperature, derivative}
    is_single_peak: bool
    quality_score: float
    grade: str
    warnings: List[str]
```

### MeltPeak

```python
@dataclass
class MeltPeak:
    temperature: float
    height: float      # Relative (0-1)
    width: float       # °C at half-max
    is_primary: bool
```

## Grading

| Grade | Score | Interpretation |
|-------|-------|----------------|
| A | ≥90 | Excellent - clean single peak |
| B | 80-89 | Good - single peak with minor issues |
| C | 70-79 | Acceptable - review recommended |
| D | 60-69 | Poor - may have non-specific products |
| F | <60 | Fail - redesign primers |

## See Also

- [Probe Binding](probe-binding.md)
- [qPCR Amplicon QC](../features/amplicon.md)
