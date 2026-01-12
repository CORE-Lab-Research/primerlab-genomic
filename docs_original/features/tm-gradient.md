# Tm Gradient Simulation (v0.4.3)

Simulate temperature gradients to find optimal annealing temperatures for primer sets.

## Overview

The Tm gradient simulation uses nearest-neighbor thermodynamics to predict primer binding efficiency across a temperature range. This helps determine:

- **Optimal annealing temperature** for maximum specificity
- **Temperature tolerance range** for each primer
- **Sensitivity analysis** to identify temperature-sensitive primers

## CLI Usage

```bash
primerlab tm-gradient --primers primers.json --min-temp 50 --max-temp 72 --step 0.5
```

### Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--primers, -p` | Path to primers JSON | Required |
| `--template, -t` | Template FASTA (optional) | None |
| `--min-temp` | Minimum temperature (°C) | 50.0 |
| `--max-temp` | Maximum temperature (°C) | 72.0 |
| `--step` | Temperature step (°C) | 0.5 |
| `--output, -o` | Output directory | tm_gradient_output |
| `--format` | Report format (markdown/json/csv) | markdown |

### Output

```
🌡️ Tm Gradient Simulation (v0.4.3)
==================================================
📂 Loading primers: primers.json
🔬 Temperature range: 50.0°C - 72.0°C (step 0.5°C)

⏳ Simulating Tm gradient for 3 primers...

==================================================
🎯 Optimal Annealing Temperature: 58.5°C
   Recommended Range: 55.0°C - 62.0°C

📊 Per-Primer Results:
   Primer1_fwd: Tm=62.3°C, Optimal=57.3°C (Grade A)
   Primer1_rev: Tm=60.8°C, Optimal=55.8°C (Grade A)
   ...

📁 Report saved to: tm_gradient_output/tm_gradient.json
```

## API Usage

```python
from primerlab.api import simulate_tm_gradient_api

primers = [
    {"name": "Gene1", "forward": "ATGCGATCGATCGATCGATCG", "reverse": "GCTAGCTAGCTAGCTAGCTAG"}
]

result = simulate_tm_gradient_api(
    primers=primers,
    min_temp=50.0,
    max_temp=72.0,
    step_size=0.5
)

print(f"Optimal annealing: {result['optimal']}°C")
print(f"Range: {result['range_min']} - {result['range_max']}°C")
```

## Thermodynamic Model

Uses Santa Lucia (1998) nearest-neighbor parameters:

- ΔH and ΔS for each dinucleotide pair
- Salt correction for Na+ concentration
- Two-state binding model for efficiency calculation

## Configuration

See `primerlab/config/tm_gradient_default.yaml` for default settings.

## See Also

- [Tutorial: Tm Gradient Simulation](../tutorials/tm-gradient.md)
- [Species Specificity](species-specificity.md)
