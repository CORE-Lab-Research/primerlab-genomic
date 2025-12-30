# TaqMan qPCR Example

Example showing TaqMan probe binding simulation.

## Files

- `probe.json` - Probe sequence
- `amplicon.fasta` - Target amplicon

## Usage

### Python API

```python
from primerlab.api import simulate_probe_binding_api

# Load probe
probe = "ATGCGATCGATCGATCGATCG"

# Simulate binding
result = simulate_probe_binding_api(probe)

print(f"Probe Tm: {result['probe_tm']:.1f}°C")
print(f"Grade: {result['grade']}")
```

## Expected Output

```
Probe Tm: 62.3°C
Optimal: 57.0°C
Grade: A
Binding Efficiency: 99.0%
```

## Probe Quality Checklist

- [x] Length 18-24 bp
- [x] GC 40-60%
- [x] Tm 68-70°C
- [x] No 5' G
