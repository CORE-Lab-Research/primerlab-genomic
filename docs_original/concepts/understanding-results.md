# Understanding Results

A comprehensive guide to interpreting PrimerLab output, scores, warnings, and recommendations.

## Quality Scores (0-100)

Every primer pair receives a quality score based on multiple factors. The score starts at 100 and penalties are applied for sub-optimal characteristics.

### Score Categories

| Score Range | Grade | Meaning | Action |
|:-----------:|:-----:|---------|--------|
| 85-100 | ✅ Excellent | Optimal design, minimal issues | Use with confidence |
| 70-84 | ✅ Good | Acceptable, minor issues | Generally safe to use |
| 50-69 | ⚠️ Fair | Notable issues detected | Review warnings carefully |
| 0-49 | ❌ Poor | Significant problems | Consider redesign |

---

## Penalty Breakdown

PrimerLab applies penalties for the following issues:

| Issue | Penalty (Standard) | What It Means |
|-------|:------------------:|---------------|
| **Primer3 Penalty** | -0 to -50 | Base penalty from thermodynamic calculations |
| **Hairpin (3' end)** | -15 | Primer folds on itself at critical 3' end |
| **Self-dimer** | -15 | Primer binds to itself |
| **Hetero-dimer** | -10 | Forward and reverse primers bind to each other |
| **Weak GC Clamp** | -15 | No G/C at 3' end (reduced specificity) |
| **Strong GC Clamp** | -5 | Too many G/C at 3' end (may cause mispriming) |
| **Poly-X Run** | -10 | Repetitive nucleotides (e.g., AAAA, GGGG) |

---

## Understanding Warnings

Warnings do not necessarily mean the primer is unusable. Use this guide to interpret them:

### ⚠️ Common Warnings

| Warning | Severity | Explanation | Recommendation |
|---------|:--------:|-------------|----------------|
| `Hairpin detected` | Medium | Secondary structure may form | Check if ΔG > -3 kcal/mol (usually OK) |
| `Self-dimer detected` | Medium | Primer may dimerize | Check if ΔG > -6 kcal/mol (usually OK) |
| `Hetero-dimer risk` | High | Primers may bind each other | Reduce primer concentration, redesign if ΔG < -8 |
| `Weak GC clamp` | Low | 3' end lacks G/C | Often acceptable for non-critical PCR |
| `Poly-X run detected` | Medium | Repetitive sequence | May cause polymerase slippage, consider masking |
| `Off-target binding` | High | BLAST found similar sequences | Verify with in-silico PCR, may need redesign |

### ✅ When Warnings Are Acceptable

1. **Hairpin ΔG > -2 kcal/mol**: The structure won't form at PCR temperatures
2. **Self-dimer ΔG > -5 kcal/mol**: Weak interaction, unlikely to compete with template
3. **Weak GC clamp on one primer only**: The other primer can compensate
4. **Poly-X of 3 or less**: Generally not problematic

---

## Key Metrics Explained

### Melting Temperature (Tm)

| Tm Difference | Status | Notes |
|:-------------:|:------:|-------|
| ≤ 2°C | ✅ Ideal | Both primers anneal at same temperature |
| 2-5°C | ⚠️ Acceptable | May need gradient PCR to optimize |
| > 5°C | ❌ Problem | One primer may not anneal efficiently |

**Recommendation**: Keep Tm between 58-62°C for standard PCR, 60-65°C for long-range.

### GC Content

| GC% | Status | Notes |
|:---:|:------:|-------|
| 40-60% | ✅ Ideal | Balanced stability |
| 30-40% or 60-70% | ⚠️ Acceptable | May need optimization |
| < 30% or > 70% | ❌ Problem | Likely unstable or too tight binding |

### Delta G (ΔG) Values

ΔG measures the stability of secondary structures. **More negative = more stable = more problematic**.

| ΔG (kcal/mol) | Interpretation |
|:-------------:|----------------|
| > -2 | ✅ No significant structure |
| -2 to -5 | ⚠️ Minor structure, usually OK |
| -5 to -8 | ⚠️ Moderate structure, may affect PCR |
| < -8 | ❌ Strong structure, likely to cause problems |

---

## QC Modes

PrimerLab supports three QC stringency levels:

| Mode | Use Case | Penalty Severity |
|------|----------|------------------|
| **strict** | Diagnostics, clinical | High penalties, low tolerance |
| **standard** | General research | Balanced |
| **relaxed** | Exploratory, difficult templates | Lower penalties |

Set in config:

```yaml
qc:
  mode: standard  # or strict, relaxed
```

---

## When to Accept vs. Reject

### ✅ Accept the Primer Pair If

- Score ≥ 70
- No ❌ (critical) warnings
- Tm difference ≤ 3°C
- In-silico PCR produces single product

### ❌ Reject and Redesign If

- Score < 50
- Multiple high-severity warnings
- Off-target amplification detected
- Tm difference > 5°C
- Product size outside expected range

---

## See Also

- [Scoring System](scoring) — Detailed algorithm explanation
- [Quality Control](../guides/quality-control) — QC workflow guide
- [Troubleshooting](../troubleshooting) — Common issues and fixes
