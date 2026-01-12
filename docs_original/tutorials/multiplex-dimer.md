# Multiplex PCR & Dimer Analysis

Guide for designing multiplex primer sets and analyzing primer dimers.

---

## Dimer Types

| Type | Description | Concern Level |
|------|-------------|:-------------:|
| **Self-dimer (Homodimer)** | Primer binds to itself | Medium |
| **Heterodimer** | Two primers bind to each other | High |
| **Hairpin** | Primer folds on itself | Low-Medium |

---

## Dimer Matrix Analysis

Check compatibility between multiple primers:

```bash
primerlab dimer-matrix --primers primers.json --format text
```

### Input Format

```json
[
  {"name": "GAPDH_F", "sequence": "ATCGATCGATCGATCGATCG"},
  {"name": "GAPDH_R", "sequence": "GCTAGCTAGCTAGCTAGCTA"},
  {"name": "ACTB_F", "sequence": "TGCATGCATGCATGCATGCA"},
  {"name": "ACTB_R", "sequence": "CGATCGATCGATCGATCGAT"}
]
```

### Output Matrix

```
Dimer Matrix (ΔG kcal/mol)
═══════════════════════════════════════
         GAPDH_F  GAPDH_R  ACTB_F  ACTB_R
GAPDH_F   -2.1     -3.5     -1.2    -0.8
GAPDH_R   -3.5     -1.8     -2.0    -4.1 ⚠️
ACTB_F    -1.2     -2.0     -1.5    -2.3
ACTB_R    -0.8     -4.1 ⚠️  -2.3    -1.9

⚠️ = ΔG < -5.0 (problematic dimer)
```

---

## Compatibility Check

Full multiplex compatibility analysis:

```bash
primerlab check-compat --primers primers.csv
```

### Features

- Cross-dimer analysis
- Tm compatibility
- Specificity overlap detection
- Multiplex scoring

---

## Python API

```python
from primerlab.core.compat_check import MultiplexValidator

primers = [
    {"name": "P1", "forward": "ATCG...", "reverse": "GCTA..."},
    {"name": "P2", "forward": "TGCA...", "reverse": "CGAT..."},
]

validator = MultiplexValidator()
result = validator.validate(primers)

print(f"Compatible: {result.is_compatible}")
print(f"Score: {result.compatibility_score}/100")
print(f"Problematic pairs: {result.problematic_dimers}")
```

---

## Multiplex Design Tips

### Tm Matching

All primers should have similar Tm (within ±2°C):

```
Good:  P1=60°C, P2=59°C, P3=61°C (Δ2°C)
Bad:   P1=60°C, P2=55°C, P3=65°C (Δ10°C)
```

### Avoid Cross-Reactivity

- Use species-check for each primer pair
- Verify no off-target binding to other amplicons

### Amplicon Size Separation

For gel visualization, use distinct sizes:

```
P1: 150 bp
P2: 250 bp  (+100)
P3: 400 bp  (+150)
```

---

## Thresholds

| Metric | Good | Warning | Fail |
|--------|:----:|:-------:|:----:|
| Heterodimer ΔG | > -5.0 | -5.0 to -7.0 | < -7.0 |
| Homodimer ΔG | > -5.0 | -5.0 to -7.0 | < -7.0 |
| Hairpin ΔG | > -2.0 | -2.0 to -4.0 | < -4.0 |
| Tm difference | < 2°C | 2-4°C | > 4°C |

---

## See Also

- [CLI: check-compat](../cli/compat_check.md)
- [CLI: dimer-matrix](../cli/README.md)
- [Features: Compatibility Check](../features/compat_check.md)
