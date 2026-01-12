# Algorithms

PrimerLab is built on top of rigorous, peer-reviewed bioinformatics algorithms.

## Primer Design Engine: Primer3

The core primer search is performed by [Primer3](https://github.com/primer3-org/primer3), the industry standard for primer design.

### How it works

1. **Scanning**: The sequence is scanned for all possible valid forward and reverse oligos based on size and Tm constraints.
2. **Filtering**: Oligos failing basic QC (GC clamp, Ns, low complexity) are discarded.
3. **Pairing**: Valid forward and reverse primers are paired to check if they generate an amplicon of the correct size.
4. **Ranking**: Pairs are ranked using the penalty method (see [Scoring](scoring.md)).

## Thermodynamics: ViennaRNA

For secondary structure prediction (hairpins, dimers), PrimerLab uses the nearest-neighbor thermodynamic model provided by [ViennaRNA](https://www.tbi.univie.ac.at/RNA/).

### Why use thermodynamics?

Simple string matching (e.g., counting matching bases) is insufficient for predicting DNA hybridization. Thermodynamics calculates the **Gibbs Free Energy (ΔG)**, which predicts the *stability* of a structure.

- **Formula**: ΔG = ΔH - TΔS
- **Interpretation**: A negative ΔG means the structure forms spontaneously. The more negative, the more stable (and problematic for primers).

## Specificity: BLAST+

For off-target checking, we use **NCBI BLAST+**.

1. **Database**: A local BLAST database is created from your reference genome.
2. **Query**: Primer sequences are blasted against this database using `blastn-short` task (optimized for short sequences).
3. **Filtering**: Hits are filtered for significant 3' end matches (the last 5-7 bases). A primer binding perfectly at the 3' end to an off-target site is considered a high-risk hit.
