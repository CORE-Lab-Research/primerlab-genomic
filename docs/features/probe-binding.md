# Probe Binding Simulation (v0.5.0)

Simulate TaqMan probe binding using nearest-neighbor thermodynamics.

## Overview

The probe binding module calculates probe-template binding characteristics:

- **Probe Tm** - Melting temperature using nearest-neighbor method
- **Binding Efficiency** - Efficiency across temperature range
- **Position Analysis** - Optimal probe placement within amplicon

## Python API

### simulate_probe_binding_api

```python
from primerlab.api import simulate_probe_binding_api

result = simulate_probe_binding_api(
    probe_sequence="ATGCGATCGATCGATCGATCG",
    amplicon_sequence="...",  # Optional
    min_temp=55.0,
    max_temp=72.0,
)

print(f"Probe Tm: {result['probe_tm']}°C")
print(f"Optimal: {result['optimal_temp']}°C")
print(f"Grade: {result['grade']}")
```

### Core Functions

```python
from primerlab.core.qpcr import (
    calculate_probe_binding_tm,
    simulate_probe_binding,
    analyze_probe_position,
    optimize_probe_position,
)

# Calculate Tm
tm = calculate_probe_binding_tm("ATGCGATCGATCGATCGATCG")

# Full simulation
result = simulate_probe_binding("ATGCGATCGATCGATCGATCG")
print(f"Binding curve: {len(result.binding_curve)} points")
```

## Probe Design Guidelines

### TaqMan Probe Requirements

| Property | Optimal | Acceptable |
|----------|---------|------------|
| Length | 18-24 bp | 15-30 bp |
| Tm | 68-70°C | 65-72°C |
| GC% | 40-60% | 30-80% |
| 5' base | Not G | Any |

### Tm Relationship

- Probe Tm should be **8-10°C higher** than primer Tm
- Ensures probe binds before primers during annealing

### 5' G Rule

Avoid G at the 5' end of the probe:

- G can quench FAM fluorescence even when free
- Reduces signal-to-noise ratio

## Output

### ProbeBindingResult

```python
@dataclass
class ProbeBindingResult:
    probe_sequence: str
    probe_tm: float
    binding_efficiency: float
    optimal_temp: float
    binding_curve: List[Dict]
    warnings: List[str]
    grade: str
    score: float
```

## See Also

- [qPCR Workflow](../tutorials/qpcr-design.md)
- [Melt Curve Analysis](melt-curve.md)
