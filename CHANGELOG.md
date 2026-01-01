# Changelog

All notable changes to PrimerLab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2026-01-01

### Added

- **Allele Discrimination / Genotyping** (`core/genotyping/`)
  - Allele-specific primer scoring engine
  - SNP position validation (3' end critical)
  - Discrimination Tm calculator
  - `score_genotyping_primer_api()` function

- **RT-qPCR Enhancements** (`core/rtpcr/`)
  - Exon junction detection for RT-specificity
  - gDNA contamination risk assessment
  - Transcript annotation loader (GTF/BED)
  - `validate_rtpcr_primers_api()` function

- **Melt Curve Visualization** (`core/qpcr/melt_plot.py`)
  - SVG melt curve plot generation
  - PNG export with matplotlib
  - Multi-peak annotation

- **CLI qPCR Commands**
  - `primerlab probe-check` - TaqMan probe binding check
  - `primerlab melt-curve` - SYBR melt curve prediction
  - `primerlab amplicon-qc` - Amplicon quality validation

### Tests

- Added 38 new tests (15 genotyping + 14 rtpcr + 9 melt plot)
- Total tests: 604

---

## [0.5.0] - 2024-12-30

### Added

- **qPCR Probe Binding Simulation** (`core/qpcr/probe_binding.py`)
  - Nearest-neighbor thermodynamic Tm calculation for probes
  - Binding efficiency simulation across temperature range
  - Optimal annealing temperature prediction
  - 5' G quenching warning

- **Probe Position Optimization** (`core/qpcr/probe_position.py`)
  - Position analysis within amplicon
  - Distance from primers validation
  - Position scoring and recommendations

- **qPCR Amplicon Validation** (`core/qpcr/amplicon_qc.py`)
  - Length validation (70-150 bp optimal)
  - GC content validation (40-60%)
  - Secondary structure penalty estimation
  - Enhanced efficiency scoring

- **SYBR Melt Curve Prediction** (`core/qpcr/melt_curve.py`)
  - Amplicon Tm prediction
  - Melt curve shape simulation
  - Multiple peak detection
  - Quality grading (A-F)

- **Melt Curve Reports** (`core/qpcr/melt_report.py`)
  - Markdown report generation
  - CSV data export
  - JSON output

- **Public API Functions**
  - `simulate_probe_binding_api()` - Probe binding simulation
  - `predict_melt_curve_api()` - Melt curve prediction
  - `validate_qpcr_amplicon_api()` - Amplicon validation

- **Documentation**
  - `docs/features/probe-binding.md`
  - `docs/features/melt-curve.md`
  - `docs/tutorials/qpcr-advanced.md`
  - `examples/qpcr_taqman/`
  - `examples/qpcr_sybr/`

- **60 new unit tests** for qPCR module

---

## [0.4.3] - 2024-12-30

### Added

- **Tm Gradient Simulation Module** (`core/tm_gradient/`)
  - Nearest-neighbor thermodynamic Tm calculation
  - Temperature gradient simulation engine
  - Optimal annealing temperature prediction
  - Temperature sensitivity analysis
  - Binding efficiency curves

- **Batch Species-Check Enhancements** (`core/species/batch/`)
  - Batch input loader (directory, multi-FASTA)
  - SQLite alignment caching with TTL
  - Parallel species analysis (ThreadPoolExecutor)
  - CSV batch export and summary reports

- **CLI Commands**
  - `primerlab tm-gradient` for temperature simulation
  - `--primers-dir`, `--parallel`, `--no-cache` for species-check

- **Public API**
  - `simulate_tm_gradient_api()` function
  - `batch_species_check_api()` function

- **Configuration**
  - `tm_gradient_default.yaml`

- **Documentation**
  - `docs/features/tm-gradient.md`
  - `docs/tutorials/tm-gradient.md`
  - `examples/tm_gradient/`

---

## [0.4.2] - 2024-12-29

### Added

- **Species Specificity Module** (`core/species/`)
  - Multi-species FASTA loader
  - Primer binding site detection across species
  - Cross-reactivity scoring (0-100 scale)
  - Specificity matrix visualization
  - Off-target species detection

- **CLI Command**
  - `primerlab species-check` for cross-species primer validation
  - `--target`, `--offtargets`, `--format` options

- **Public API**
  - `check_species_specificity_api()` function
  
- **Documentation**
  - `docs/features/species-specificity.md`
  - ViennaRNA installation instructions

### Changed

- Updated README badges and features for v0.4.2

---

## [0.4.1] - 2024-12-26

### Added

- **Amplicon Analysis Module** (`core/amplicon/`)
  - Secondary structure prediction (ViennaRNA with fallback)
  - GC profile visualization (50bp window)
  - GC clamp analysis (5nt at ends)
  - Amplicon Tm prediction (nearest-neighbor)
  - Restriction site mapping (6 common enzymes)
  - Amplicon quality scoring (0-100, A-F grade)

- **CLI Flags**
  - `--amplicon-analysis` for `primerlab run`
  - `--template` for `primerlab check-compat` (overlap analysis)

- **Public API**
  - `analyze_amplicon()` function
  - `run_overlap_simulation()` function

- **Reports**
  - Amplicon JSON, Markdown, Excel reports
  - Overlap analysis JSON report

---

## [0.4.0] - 2024-12-25

### Added

- **Primer Compatibility Check Module** (`core/compat_check/`)
  - Cross-dimer detection between primer pairs
  - Tm uniformity scoring across sets
  - GC content consistency check
  - Multiplex compatibility scoring

- **CLI Command**
  - `primerlab check-compat` for primer set analysis
  - Excel and IDT plate export

- **In-silico Overlap Detection**
  - Virtual PCR simulation with overlap warnings
  - Multi-amplicon clash detection

- **Documentation**
  - `docs/features/compat_check.md`

### Changed

- Renamed internal module from `multiplex` to `compat_check`

---

## [0.3.5] - 2025-12-24

### Added

- **Tutorials** (`docs/tutorials/`)
  - Quick Start guide
  - PCR Walkthrough
  - qPCR Design
  - Off-target Tutorial
- **API Reference** (`docs/api/`)
  - public.md, insilico.md, report.md, models.md
- **Troubleshooting** (`docs/troubleshooting.md`)
- **Presets Documentation** (`docs/configuration/presets.md`)
- **Architecture Overview** (`docs/architecture.md`)
- `docs/features/report-generation.md`
- `docs/features/offtarget-detection.md`

### Changed

- Enhanced `README.md` with documentation table
- Updated `RELEASE_NOTES.md` to v0.3.5
- Updated `docs/cli/run.md` with --validate, --blast, --report flags
- Updated `docs/configuration/README.md` with offtarget/report sections
- Fixed broken links in `docs/features/README.md`
- Removed future/placeholder references

---

## [0.3.4] - 2025-12-24

### Added

- **Tm Correction for Mismatches** (`binding.py:calculate_corrected_tm`)
  - Configurable correction per mismatch (default: 2.5°C)
  - Weighted: 3' mismatches count 2x more
- **3' Stability Warning** (`binding.py:check_three_prime_stability`)
  - Warning jika ΔG < -9 (too stable) atau > -3 (too weak)
  - Configurable thresholds

### Changed

- Integrated new functions into `analyze_binding()`
- Exported new functions from `insilico/__init__.py`

---

## [0.3.3] - 2025-12-24

### Added

- **Report Generation Module** (`core/report/`)
  - `PrimerReport` and summary dataclasses (`models.py`)
  - `ReportGenerator` dengan method chaining (`generator.py`)
  - ASCII alignment visualization (`alignment_view.py`)
  - HTML export dengan dark/light mode toggle (`html_export.py`)
  - JSON export dengan filtering options (`json_export.py`)
  - Unified `ReportExporter` class

- **CLI Report Integration**
  - `--report` flag untuk generate enhanced report
  - `--report-format` (markdown, html, json)
  - `--report-output` untuk custom output path

### Changed

- Fixed all skipped tests (blast_cache, parallel_blast)
- Added `freezegun` as dev dependency
- Updated STRUCTURE.md with report module

### New CLI Flags

```bash
primerlab run --config my.yaml --report --report-format html --report-output report.html
```

---

## [0.3.2] - 2025-12-22

### Added

- **NCBI Web BLAST Fallback** (`tools/ncbi_blast.py`)
  - `--online` flag to force NCBI web BLAST
  - Rate limiting for web requests
- **Colored CLI Output** (`cli/formatter.py`)
  - Grade colors (A=green, F=red)
  - Output verbosity levels
- **BLAST Cache** (`tools/blast_cache.py`)
  - SQLite-based result caching with TTL
  - `--no-cache` flag to skip cache
- **Progress Indicators** (`cli/progress.py`)
  - Spinner and progress bar with ETA
- **Parallel BLAST** (`tools/parallel_blast.py`)
  - Multi-threaded batch processing
  - `--threads` option
- **Config Validation** (`config_validator.py`)
  - Helpful error messages for offtarget config

### New CLI Flags

```bash
primerlab blast --online --verbose --no-cache --threads 4 --timeout 300
```

---

## [0.3.1] - 2025-12-21

### Added

- **Complete BLAST Integration**
  - `--blast` and `--blast-db` flags for `primerlab run` command
  - `offtarget:` config section in YAML files
  - `check_offtargets()` public API function
  - `--batch`, `--db-info`, `--variants`, `--maf-threshold` CLI flags
- **SNP/Variant Check**
  - VCF parser with gzip support and MAF filtering (`tools/vcf_parser.py`)
  - BED parser for region filtering (`tools/bed_parser.py`)
  - Primer-SNP overlap detection with 3' impact assessment
  - Variant data models with impact levels (HIGH/MEDIUM/LOW)
- **Documentation**
  - `docs/cli/blast.md` - BLAST command usage
  - `examples/workflow_blast_variant.md` - End-to-end workflow

### New CLI Usage

```bash
primerlab run --config my.yaml --blast --blast-db genome.fasta
primerlab blast --db-info -d genome.fasta
primerlab blast -p primers.fasta -d genome.fasta --variants snps.vcf
```

---

## [0.3.0] - 2025-12-21

### Added

- **BLAST Integration** for off-target detection
- `primerlab blast` CLI command for primer specificity check
- `BlastWrapper` class with BLAST+ auto-detection
- `BiopythonAligner` fallback using `Bio.Align.PairwiseAligner`
- `PrimerAligner` unified interface (auto-selects BLAST+ or Biopython)
- `OfftargetFinder` for off-target binding site detection
- `SpecificityScorer` with grades (A-F) and risk levels
- `IntegratedPCRResult` combining in-silico and off-target results
- `specificity_report.md` and `blast_result.json` outputs
- Test database `examples/blast/test_db.fasta`

### New CLI Usage

```bash
primerlab blast -p primers.fasta -d database.fasta
primerlab blast -p "ATGC...,GCAT..." -d genome.fasta --target gene_x
```

---

## [0.2.5] - 2025-12-20

### Added

- Primer-dimer check between forward and reverse primers
- `check_primer_dimer()` function in binding module
- Extension time estimation for amplicons (1 min/kb)
- Primer-dimer section in markdown report
- Extension time in product details

### Changed

- `InsilicoPCRResult` now includes `primer_dimer` field
- `AmpliconPrediction` now includes `extension_time_sec` field

---

## [0.2.4] - 2025-12-20

### Added

- `--circular` flag for `primerlab insilico` command to treat templates as circular
- Version bump from 0.2.0 to 0.2.4
- `auto_validate` config option support in `advanced` section
- Validation results included in `result.json` output
- Documentation for `insilico` command

### Changed

- Improved in-silico output formatting

---

## [0.2.3] - 2025-12-19

### Added

- `--validate` / `-V` flag for `primerlab run pcr/qpcr` command
- `validate_primers()` function in public API (`primerlab.api.public`)
- `validate=True` parameter for `design_pcr_primers()` and `design_qpcr_assays()`
- In-silico validation results automatically added to workflow metadata

### Changed

- API functions now return validation data when enabled

---

## [0.2.2] - 2025-12-19

### Added

- Markdown report generation (`insilico_report.md`)
- Amplicon FASTA export (`predicted_amplicons.fasta`)
- Enhanced console alignment visualization
- Report module (`primerlab/core/insilico/report.py`)

### Changed

- CLI uses new report module for all insilico output
- Improved console formatting for binding results

---

## [0.2.1] - 2025-12-19

### Added

- IUPAC degenerate base support (R, Y, S, W, K, M, B, D, H, V, N)
- `bases_match()` function with IUPAC-aware comparison
- Circular template binding detection (across start-end boundary)
- Weighted likelihood scoring (3' mismatches penalized more)
- Centralized `reverse_complement()` supporting all IUPAC codes
- WSL-specific installation documentation

### Changed

- Moved `reverse_complement()` from binding.py/engine.py to sequence.py
- Updated tests for IUPAC compatibility

---

## [0.2.0] - 2025-12-18

### Added

- In-silico PCR simulation engine
- `primerlab insilico` CLI command
- Primer binding site analysis with Tm calculation
- Amplicon prediction with likelihood scoring
- Virtual PCR workflow (`InsilicoPCR` class)
- Support for JSON and FASTA primer input

### Changed

- Major version for new core feature

---

## [0.1.6] - 2025-12-17

### Added

- `primerlab stats` command for sequence analysis
- `--quiet` flag to suppress non-essential output
- Primer database integration (`primerlab history`)
- GC profile visualization (`primerlab plot`)

### Fixed

- Flaky CLI integration tests
- Deprecation warnings cleanup

---

## [0.1.5] - 2025-12-16

### Added

- Multi-FASTA batch processing (`primerlab batch-run --fasta`)
- Region masking support (`--mask` flag)
- Primer comparison tool (`primerlab compare`)
- Preset management (`primerlab preset list/show`)
- Config validation (`primerlab validate`)
- Export to vendor formats (IDT, Sigma, Thermo)

### Changed

- Improved batch summary reports

---

## [0.1.4] - 2025-12-15

### Added

- Enhanced error messages
- Audit log generation
- Result metadata

---

## [0.1.3] - 2025-12-14

### Added

- Multi-candidate reranking engine
- Custom primer naming patterns
- `primerlab health` command
- `primerlab init` command for template generation
- Rich console output

---

## [0.1.2] - 2025-12-13

### Added

- YAML configuration support
- Default config files for pcr/qpcr workflows

---

## [0.1.1] - 2025-12-12

### Fixed

- Installation issues
- Documentation updates

---

## [0.1.0] - 2025-12-11

### Added

- Initial release
- PCR primer design workflow
- qPCR assay design with probe
- Primer3-py integration
- Basic QC checks
