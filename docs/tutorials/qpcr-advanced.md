# Advanced qPCR Features Tutorial (v0.5.0)

Learn how to use PrimerLab's advanced qPCR simulation features.

## What You'll Learn

1. TaqMan probe binding simulation
2. SYBR Green melt curve prediction
3. qPCR amplicon quality assessment

## Prerequisites

- PrimerLab v0.5.0+
- Basic qPCR understanding

---

## 1. TaqMan Probe Binding Simulation

### Objective

Simulate probe-template binding to ensure optimal annealing.

### Step 1: Prepare Your Probe

```python
probe = "ATGCGATCGATCGATCGATCG"  # Your TaqMan probe sequence
```

### Step 2: Run Simulation

```python
from primerlab.api import simulate_probe_binding_api

result = simulate_probe_binding_api(
    probe_sequence=probe,
    min_temp=55.0,
    max_temp=72.0,
)

print(f"Probe Tm: {result['probe_tm']:.1f}°C")
print(f"Optimal annealing: {result['optimal_temp']:.1f}°C")
print(f"Grade: {result['grade']}")
```

### Step 3: Analyze Position (Optional)

```python
amplicon = "NNNNN" + probe + "NNNNN"  # Your amplicon

result = simulate_probe_binding_api(
    probe_sequence=probe,
    amplicon_sequence=amplicon,
)

if "position" in result:
    print(f"Probe start: {result['position']['probe_start']}")
    print(f"Position score: {result['position']['position_score']}")
```

### Expected Output

```
Probe Tm: 68.5°C
Optimal annealing: 60.0°C
Grade: A
```

---

## 2. SYBR Green Melt Curve Prediction

### Objective

Predict melt curve to check for non-specific products.

### Step 1: Prepare Amplicon

```python
amplicon = "ATGCGATCGATCGATCGATCG" * 5  # 100bp amplicon
```

### Step 2: Predict Melt Curve

```python
from primerlab.core.qpcr import predict_melt_curve

result = predict_melt_curve(amplicon)

print(f"Predicted Tm: {result.predicted_tm:.1f}°C")
print(f"Single peak: {result.is_single_peak}")
print(f"Grade: {result.grade}")
```

### Step 3: Generate Report

```python
from primerlab.core.qpcr import generate_melt_markdown

md_report = generate_melt_markdown(result)
print(md_report)
```

### Expected Output

```
Predicted Tm: 81.5°C
Single peak: True
Grade: A
```

---

## 3. qPCR Amplicon Quality Check

### Objective

Validate amplicon for qPCR suitability.

### Step 1: Check Amplicon

```python
from primerlab.core.qpcr import validate_qpcr_amplicon

amplicon = "ATGC" * 25  # 100bp

result = validate_qpcr_amplicon(amplicon)

print(f"Length OK: {result.length_ok}")
print(f"GC OK: {result.gc_ok}")
print(f"Quality: {result.quality_score:.1f}")
```

### Step 2: Check Warnings

```python
if result.warnings:
    print("Warnings:")
    for w in result.warnings:
        print(f"  - {w}")
```

---

## Complete Workflow

### TaqMan qPCR Design Validation

```python
from primerlab.api import simulate_probe_binding_api
from primerlab.core.qpcr import (
    validate_qpcr_amplicon,
    score_qpcr_efficiency,
)

# Your sequences
fwd_primer = "ATGCGATCGATCGATCG"
rev_primer = "CGATCGATCGATCGATC"
probe = "GATCGATCGATCGATCGATC"
amplicon = "..."  # Full amplicon sequence

# 1. Check amplicon quality
amp_result = validate_qpcr_amplicon(amplicon)
print(f"Amplicon Grade: {amp_result.grade}")

# 2. Simulate probe binding
probe_result = simulate_probe_binding_api(probe, amplicon)
print(f"Probe Grade: {probe_result['grade']}")

# 3. Estimate efficiency
efficiency = score_qpcr_efficiency(
    amplicon_length=len(amplicon),
    primer_tm_diff=0.5,  # |Fwd Tm - Rev Tm|
    probe_tm_diff=probe_result['probe_tm'] - 60.0,
)
print(f"Efficiency: {efficiency:.1f}%")
```

---

## Tips

1. **Probe Tm**: Should be 8-10°C higher than primers
2. **Amplicon Length**: 70-150 bp optimal for qPCR
3. **GC Content**: 40-60% for reliable amplification
4. **5' G Rule**: Avoid G at probe 5' end

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Low probe score | Check Tm, length, 5' base |
| Multiple melt peaks | Redesign primers |
| Low efficiency | Shorten amplicon, balance Tms |

## See Also

- [Probe Binding Feature](../features/probe-binding.md)
- [Melt Curve Feature](../features/melt-curve.md)
