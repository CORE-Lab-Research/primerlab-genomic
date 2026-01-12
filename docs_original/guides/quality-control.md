# Quality Control (QC)

PrimerLab enforces strict quality control on all designed primers to ensure experimental success.

## QC Metrics

Every primer candidate undergoes the following checks:

### 1. Melting Temperature (Tm)

- **Why it matters**: Determines the annealing temperature of the reaction. Forward and Reverse primers must have similar Tms (within 2°C) to anneal efficiently at the same step.
- **Method**: Calculated using nearest-neighbor thermodynamics (SantaLucia 1998).
- **Optimization**: PrimerLab aims for the `opt` Tm specified in your config (default ~60°C).

### 2. GC Content

- **Why it matters**: Affects stability and binding kinetics. extremely high GC (>65%) or low GC (<35%) can cause secondary structures or non-specific binding.
- **Target**: 40-60% is ideal.

### 3. Secondary Structures

PrimerLab checks for three types of unwanted structures using thermodynamic alignment:

#### Self-Dimers

- **What**: A primer binding to another copy of itself.
- **Impact**: Consumes primer, reduces yield, creates "primer dimer" bands.
- **Metric**: Delta G (Gibbs Free Energy). More negative = more stable (bad). Default threshold is > -5 kcal/mol.

#### Hetero-Dimers (Cross-Dimers)

- **What**: Forward primer binding to the Reverse primer.
- **Impact**: High risk of creating empty amplicons.
- **Metric**: Delta G. Default threshold is > -6 kcal/mol.

#### Hairpins

- **What**: A primer folding back on itself.
- **Impact**: Prevents primer from binding to the template.
- **Metric**: Delta G. Default threshold is > -2 kcal/mol.

### 4. 3' End Stability

- **Why it matters**: The last 5 bases at the 3' end are critical for DNA polymerase initiation.
- **Check**:
  - Avoid "GC clamp" (too many G/Cs at the very end).
  - Avoid "Poly-X" runs (e.g., GGGGG or TTTTT).
  - Avoid complementary 3' ends between pairs.

---

## Amplicon QC

We also check the product (amplicon) itself:

- **Length**: Must be within the specified range.
- **GC Content**: balanced GC ensures partial melting during denaturation.
- **Complexity**: Low-complexity regions (repeats) are flagged.

---

## Interpreting QC Warnings

| Warning | Action |
|---------|--------|
| `High Loop Tm` | The hairpin is very stable. Increase annealing temp or redesign. |
| `3' Stability` | The 3' end is too sticky. Add an A/T base to the 3' end if identifying manually. |
| `Product Too Large` | Efficiency may drop. Increase extension time. |
