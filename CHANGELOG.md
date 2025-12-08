# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.3] - 2025-12-08
### Added
- **Multi-Candidate Re-ranking Engine**:
    - Requests N candidates from Primer3 (configurable, default: 50).
    - Evaluates each with ViennaRNA QC (hairpin, homodimer, heterodimer).
    - Selects best primer pair that passes all QC checks.
    - Configurable `qc_mode`: strict (-6.0), standard (-9.0), relaxed (-12.0).
    - Includes alternative primers section in reports.
- **Sequence QC Enhancements**:
    - GC Clamp check (3' end stability, last 5 bases).
    - Poly-X run detection (max 4 consecutive identical bases).
- **New Workflow Presets**:
    - `dna_barcoding` preset (400-700bp amplicons, relaxed QC).
    - `rt_pcr` preset (80-200bp amplicons, tight Tm).
    - `long_range` preset (3-10kb amplicons, strict QC).
- **CLI Enhancements**:
    - `primerlab init` command to generate template config.
    - `primerlab health` command to check all dependencies.
    - `--export` flag for vendor format selection (idt, sigma, thermo).
    - Colorized terminal output (Rich).
    - Progress bars for batch processing (tqdm).
- **Configuration Options**:
    - `advanced.seed` parameter for reproducible primer selection.
    - `output.export_formats` in config file.
- **Documentation**:
    - Troubleshooting guide.
    - QC metrics guide with scientific references.
    - Re-ranking algorithm documentation.

### Improved
- Exception classes now follow standardized error codes per `error-codes.md`.
- Logger now includes workflow context in log messages.
- Config validation with soft warnings for suboptimal settings.

### Fixed
- ViennaRNA fallback handling for systems without ViennaRNA installed.

## [0.1.2] - 2025-12-07
### Added
- **Example Packages**:
    - 4 ready-to-use config examples (`pcr_standard.yaml`, `pcr_long_range.yaml`, `qpcr_taqman.yaml`, `qpcr_sybr.yaml`).
    - Batch sequences CSV example for batch processing.
    - Examples README with usage instructions.
- **Enhanced Error Handling**:
    - Minimum sequence length validation (50 bp).
    - Detailed Primer3 failure reasons (shows why primers couldn't be found).
    - Config validation with clear, actionable error messages.
    - Workflow type validation (pcr/qpcr only).
    - Tm and product_size range validation (min < max).
- **Output Enhancements**:
    - CSV export for primers (`primers.csv`).
    - Vendor ordering format export (IDT, Sigma, Thermo).
    - ASCII amplicon visualizer in reports.
    - Summary statistics table (Average Tm, GC%, Amplicon Size, QC Status).
    - Primer Candidate Statistics showing Primer3 rejection reasons.
- **CLI Improvements**:
    - `--dry-run` flag to validate config without running workflow.
    - `batch-generate` command to generate multiple configs from CSV.

### Improved
- Error messages now include specific suggestions for troubleshooting.
- Report metadata now uses dynamic version from package.

## [0.1.1] - 2025-11-30
### Added
- **Configuration Enhancements**:
    - `product_size` parameter with simplified syntax (`min`, `opt`, `max`).
    - Preset configuration support (`preset: "long_range"`, `"standard_pcr"`).
- **qPCR Enhancements**:
    - Explicit `mode` parameter (`sybr` or `taqman`).
    - `mode: sybr` automatically disables probe design.

### Fixed
- `SetuptoolsDeprecationWarning` regarding license format in `pyproject.toml`.

## [0.1.0] - 2025-11-27
### Added
- **Core Framework**:
    - Modular 3-layer architecture (CLI, Workflows, Core).
    - Unified YAML configuration system.
    - Robust logging and progress tracking.
- **PCR Workflow**:
    - Automated primer design using Primer3.
    - Comprehensive QC (Tm, GC, Hairpin, Homodimer, Heterodimer).
    - JSON and Markdown report generation.
- **qPCR Workflow**:
    - TaqMan® probe design support.
    - Primer-Probe compatibility checks.
    - Efficiency estimation logic.
- **API**:
    - Programmatic access via `primerlab.api.public`.
    - Functions: `design_pcr_primers`, `design_qpcr_assays`.
- **Testing**:
    - Full pytest suite covering PCR, qPCR, and API.
    - CI/CD integration via GitHub Actions.

### Fixed
- Critical bug in reverse primer coordinate calculation (Primer3 3' index vs 5' start).
- QC silent pass bug when ViennaRNA is missing (now raises explicit warnings).
- Timeout handling for stuck Primer3 processes.

### Changed
- Switched to `pyproject.toml` for modern packaging (PEP 621).
- Updated documentation structure for long-term roadmap.
