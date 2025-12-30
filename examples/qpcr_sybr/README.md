# SYBR Green qPCR Example

Example showing SYBR Green melt curve prediction.

## Files

- `amplicon.fasta` - Target amplicon

## Usage

### Python API

```python
from primerlab.core.qpcr import predict_melt_curve, generate_melt_markdown

# Load amplicon (100bp example)
amplicon = "ATGCGATCGATCGATCGATCG" * 5

# Predict melt curve
result = predict_melt_curve(amplicon)

print(f"Predicted Tm: {result.predicted_tm:.1f}°C")
print(f"Single peak: {result.is_single_peak}")
print(f"Grade: {result.grade}")

# Generate report
print(generate_melt_markdown(result))
```

## Expected Output

```
Predicted Tm: 73.7°C
Single peak: True
Grade: A
Warnings: []
```

## Melt Curve Quality Checklist

- [x] Amplicon 70-150 bp
- [x] GC 40-60%
- [x] Single peak predicted
- [x] Grade A or B
