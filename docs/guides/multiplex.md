# Multiplex PCR & Compatibility

Design and validate primers for Multiplex PCR, where multiple targets are amplified in a single reaction.

## Overview

Multiplex PCR saves time and reagents but requires careful primer design to prevent:

- **Primer Dimers**: Primers binding to each other.
- **Cross-Reactivity**: Primers amplifying off-target regions.
- **Competition**: One target amplifying much more efficiently than others.

---

## Workflow

### 1. Design Individual Pairs

First, design primers for each target independently. **Crucial**: Use the same melting temperature (Tm) settings for all targets.

```yaml
# shared_params.yaml - Use for all targets
parameters:
  tm:
    min: 59.0
    opt: 60.0
    max: 61.0  # Narrow range is best for multiplexing
  gc:
    min: 40.0
    max: 60.0
```

Run the design for each target:

```bash
primerlab run pcr --config shared_params.yaml --sequence target1.fasta --out target1/
primerlab run pcr --config shared_params.yaml --sequence target2.fasta --out target2/
```

### 2. Check Compatibility

Use the `check-compat` command to analyze multiple primer files together.

```bash
primerlab check-compat \
  -p target1/primers.json \
  -p target2/primers.json \
  --multiplex
```

### 3. Analyze Results

The tool calculates a **Compatibility Score** based on:

- **Self-Dimers**: Primers binding to themselves.
- **Hetero-Dimers**: Forward from Pair A binding to Reverse from Pair B.
- **3' End Complementarity**: Analyzing the critical 3' region for extension.

**Scoring Guide:**

- **90-100**: Excellent (No significant interactions)
- **80-89**: Good (Minor interactions, likely negligible)
- **< 80**: Risky (High probability of dimers, redesign recommended)

---

## Troubleshooting Multiplex Reactions

| Issue | Solution |
|-------|----------|
| **Uneven Amplification** | Adjust primer concentrations (increase for weak products). Ensure amplicon sizes are different enough to separate on gel/CE. |
| **Missing Bands** | Check for primer dimers consuming reagents. Redesign the failing set. |
| **Non-Specific Bands** | Increase annealing temperature or perform a "Species Specificity" check. |

## Feature: Dimer Matrix

For complex multiplex sets (>4 pairs), generate a visual matrix:

```bash
primerlab check-compat --primers all_primers.json --plot-matrix dimer_matrix.png
```

This creates a heatmap showing interaction strength (Delta G) between every combination of primers.
