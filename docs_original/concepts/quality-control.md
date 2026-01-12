# Quality Control

How PrimerLab evaluates and scores primers.

## Scoring System

Each primer pair receives a score from 0-100 based on multiple factors:

| Factor | Weight | Description |
|--------|:------:|-------------|
| Tm match | 25% | Closeness to optimal Tm |
| GC content | 20% | Within 40-60% range |
| Self-dimer | 20% | Low self-complementarity |
| Hairpin | 15% | Low secondary structure |
| 3' stability | 10% | Appropriate 3' end |
| Pair balance | 10% | Tm difference between primers |

---

## Melting Temperature (Tm)

### Calculation Method

PrimerLab uses the nearest-neighbor thermodynamic model:

```
Tm = ΔH / (ΔS + R × ln(Ct/4)) - 273.15 + salt_correction
```

Where:

- ΔH = Enthalpy of duplex formation
- ΔS = Entropy
- R = Gas constant (1.987 cal/mol·K)
- Ct = Primer concentration

### Salt Correction

Accounts for ionic strength:

```yaml
parameters:
  salt:
    monovalent: 50.0    # mM (Na+, K+)
    divalent: 1.5       # mM (Mg2+)
    dntp: 0.2           # mM
```

### Recommendations

| Application | Optimal Tm |
|-------------|:----------:|
| Standard PCR | 58-62°C |
| Long-range PCR | 62-68°C |
| Colony PCR | 55-60°C |
| qPCR | 58-62°C |

---

## GC Content

### Optimal Range

**40-60%** is ideal for:

- Primer stability
- Uniform melting
- Reduced secondary structures

### GC Clamp

3' end should have 1-2 G or C bases for stable binding, but avoid:

- More than 3 G/C at 3' end (non-specific priming)
- G runs (self-complementarity)

---

## Self-Dimers

Primers that bind to themselves reduce effective concentration.

### Thermodynamic Threshold

| Structure | ΔG Threshold |
|-----------|:------------:|
| Self-dimer | > -5 kcal/mol |
| 3' self-dimer | > -3 kcal/mol |

### Example

```
5'- ATGCGATCGAT -3'
        ||||
3'- TAGCTAGCGTA -5'   Self-dimer
```

---

## Hairpins

Intramolecular secondary structures reduce primer availability.

### Threshold

**ΔG > -2 kcal/mol** (less stable = better)

### Visualization

```
    A
   / \
  T   G
  |   |
  A   C
   \ /
    T
   ...
5'-ATGC-3'   Hairpin structure
```

---

## Hetero-dimers (Cross-dimers)

Forward and reverse primers binding to each other.

### Threshold

**ΔG > -5 kcal/mol**

### Check

```bash
primerlab check-compat -p primers.json
```

---

## 3' End Stability

The 3' end is critical for specificity:

### Rules

1. **Avoid runs of G or C** — Can cause non-specific binding
2. **1-2 G/C at 3' end** — Provides stability (GC clamp)
3. **Avoid T at 3' end** — Less stable

### Scoring

| 3' Pattern | Score Impact |
|------------|:------------:|
| 1-2 G/C | +10% |
| 3+ G/C run | -15% |
| Ends with T | -5% |

---

## Pair Balance

Forward and reverse primers should have similar Tm:

| Tm Difference | Quality |
|:-------------:|---------|
| < 1°C | Excellent |
| 1-2°C | Good |
| 2-4°C | Acceptable |
| > 4°C | Poor |

---

## Amplicon Quality

For qPCR especially:

| Parameter | Optimal |
|-----------|:-------:|
| Length | 70-150 bp |
| GC content | 40-60% |
| Secondary structure | Minimal |

### Check Amplicon

```bash
primerlab amplicon-qc --amplicon output/amplicon.fasta
```

---

## See Also

- [Configuration Reference](../reference/config.md) — Adjust thresholds
- [Primer Design Logic](primer-design.md) — How candidates are generated
