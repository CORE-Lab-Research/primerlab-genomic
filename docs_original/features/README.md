# Features

Advanced features in PrimerLab Genomic.

## Feature Overview

### 🧬 Core Design Capabilities

These features are the foundation of PrimerLab's design engine:

- **[Batch Processing](batch-processing.md)**  
  Design primers for multiple target sequences in a single run. Supports FASTA input and parallel processing.

- **[Tm Gradient Simulation](tm-gradient.md)**  
  Simulate PCR performance across a range of annealing temperatures to find the optimal thermal cycling conditions.

- **[Species Specificity](species-specificity.md)**  
  Ensure your primers bind only to the target species by cross-referencing against background genomes (e.g., Human vs. Pathogen).

- **[Region Masking](masking.md)**  
  Exclude specific regions (e.g., repeating elements, conserved domains) from design consideration.

- **[Sequence Handling](sequence-handling.md)**  
  Robust support for IUPAC ambiguity codes and automatic handling of RNA input sequences.

### 🔍 Analysis & QC

Validate your designs before ordering synthesis:

- **[Off-target Detection](offtarget-detection.md)**  
  BLAST-based analysis to identify potential non-specific amplifications in the background genome.

- **[In-silico PCR](../cli/insilico.md)**  
  Virtual amplification simulation to predict amplicon size and specificity.

- **[Primer Compatibility Check](compat_check.md)**  
  Analyze primer pairs for cross-dimers and self-dimers to prevent experimental failure.

- **[Amplicon Analysis](amplicon.md)**  
  Verify amplicon characteristics including GC content, secondary structures, and length constraints.

### 🧪 Advanced qPCR & Probes

Specialized tools for quantitative PCR:

- **[Probe Binding Simulation](probe-binding.md)**  
  Calculate thermodynamic properties for TaqMan probes to ensure efficient binding.

- **[Melt Curve Prediction](melt-curve.md)**  
  Simulate SYBR Green melt curves to distinguish specific products from artifacts.

- **[RT-qPCR Validation](rtpcr.md)**  
  Design primers spanning exon-exon junctions to avoid amplification of genomic DNA.

### 🛠️ System & Utilities

- **[Report Generation](report-generation.md)**  
  Export results in comprehensive Markdown, HTML, or machine-readable JSON formats.

- **[Allele Discrimination](genotyping.md)**  
  Scoring system for SNP genotyping primers to maximize discrimination capability.

- **[Design History](../cli/history.md)**  
  Local SQLite database tracks every design run for complete reproducibility.
