# Changelog

All notable changes to PrimerLab will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
