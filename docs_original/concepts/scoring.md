# Scoring System

Understanding how PrimerLab ranks primer candidates from 0 to 100.

## The Design Philosophy

PrimerLab uses a **penalty-based scoring system**. Every primer pair starts with a conceptual score of 0 (perfect) penalty, and accumulates penalties for deviations from optimal parameters.

For user display, these penalties are converted to a 0-100 Quality Score, where 100 is perfect.

---

## Scoring Factors

The total score is a weighted sum of deviations for the following factors:

### 1. Tm Deviation (Weight: 25%)

How far is the primer's Tm from the `opt_tm` setting?

- **Optimality**: Perfect match = 0 penalty.
- **Penalty**: Increases as Tm moves away from optimum.
- **Pair Difference**: Large difference between Forward and Reverse Tm incurs a heavy penalty.

### 2. GC Content (Weight: 20%)

How close is the GC% to 50%?

- **Optimality**: 50% = 0 penalty.
- **Range**: Deviations outside 40-60% incur increasing penalties.

### 3. Self-Complementarity (Weight: 20%)

Does the primer bind to itself?

- **Metric**: Alignment score / Delta G.
- **Penalty**: High affinity self-binding = high penalty.

### 4. Pair Complementarity (Weight: 20%)

Do the Forward and Reverse primers bind to each other?

- **Metric**: Alignment score / Delta G.
- **Penalty**: This is weighted heavily because primer-dimers ruin experiments.

### 5. Product Size (Weight: 5%)

is the amplicon length close to `opt_product_size`?

- Less critical than thermodynamic properties, but useful for optimization.

### 6. 3' End Stability (Weight: 10%)

Is the 3' end stable but not *too* sticky?

- Penalties for G/C runs at the 3' tip.

---

## Quality Grade Scale

| Score | Grade | Interpretation |
|-------|:-----:|----------------|
| **95-100** | ⭐ Excellent | Almost theoretical perfection. Rare. |
| **90-94** | ✅ Great | Standard stringent result. Highly reliable. |
| **80-89** | 👌 Good | Likely to work well. Minor deviations. |
| **70-79** | ⚠️ Fair | May require optimization (Mg++, Temp). |
| **< 70** | ❌ Poor | Significant risk of failure. Try to redesign. |

## Customizing Weights

*(Advanced)* You can tweak these weights in your configuration if you prioritize one factor over others (e.g., strict Tm over GC%):

```yaml
scoring:
  weights:
    tm: 0.4
    gc: 0.1
    dimer: 0.3
    compl: 0.2
```
