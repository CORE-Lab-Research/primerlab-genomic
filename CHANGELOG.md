# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-12-18

### Added

- **In-silico PCR Simulation** (NEW):
  - `primerlab insilico` CLI command for primer validation.
  - Virtual PCR engine with primer binding detection.
  - Multi-product prediction with likelihood scoring.
  - Binding site analysis (3' match, 5' mismatch tolerance, Tm).
  - Outputs: `insilico_result.json`, `predicted_amplicons.fasta`.
  - Primer alignment visualization in terminal.
  - Example files: `examples/insilico/primers.json`, `template.fasta`.

### Improved

- **YAML Error Handling**:
  - Shows line number, column, and problematic content.
  - Lists common YAML syntax errors with fixes.
- **Database Resilience**:
  - SQLite integrity check on startup.
  - Auto-backup before repair operations.
  - Auto-recovery from corruption.

### Added Tests

- 24 new unit tests for in-silico PCR engine.
- CLI integration tests for `primerlab insilico`.
- Total: 220+ tests passing.

## [0.1.6] - 2025-12-18

### Added

- **`primerlab stats` command** (NEW):
  - Quick sequence analysis before primer design.
  - Shows: length, GC%, AT%, N-masked count, IUPAC codes.
  - JSON output with `--json` flag.
  - Warns if sequence is too short or has issues.
- **Version check in `primerlab health`**:
  - Automatically checks GitHub for newer releases.
  - Shows update instructions if available.
- **`--quiet` flag for `run` command**:
  - Suppresses info/warning messages.
  - Only shows errors and final output.
- **IUPAC Ambiguous Codes Support**:
  - Codes (R, Y, W, S, K, M, B, D, H, V) auto-converted to N.
  - Warning displayed to user.
  - Regions excluded from primer placement.
- **RNA Sequence Detection**:
  - Uracil (U) auto-converted to Thymine (T).
  - Warning displayed to user.
- **Comprehensive Test Suite**:
  - 70+ unit tests covering all core modules.
  - 10 integration tests (E2E for PCR, qPCR, batch).
  - 8 stats command tests.
  - Total: 196+ tests passing.
- **Test Fixtures**:
  - `examples/multi_sequences.fasta` - 10 housekeeping genes.
  - `examples/masked_sequence.fasta` - N-masked regions.
  - `examples/excluded_regions.bed` - BED file example.
  - `tests/fixtures/sample_result.json` - Result fixture.

### Improved

- Better sequence validation with descriptive error messages.
- Matplotlib now a required dependency (for `primerlab plot`).

### Dependencies

- Added `matplotlib>=3.5.0` to required dependencies.

## [0.1.5] - 2025-12-17

### Added

- **Auto Parameter Suggestion**:
  - Analyzes Primer3 failure reasons (Tm, GC, product size, probe).
  - Suggests relaxed parameters when design fails.
  - Shows actionable suggestions in CLI output.
- **Primer Comparison Tool** (`primerlab compare`):
  - Compare two primer design results side-by-side.
  - Shows quality scores, Tm balance, GC content, hairpin/dimer ΔG.
  - Determines winner and lists pros/cons for each.
  - Supports custom labels: `--labels Design1,Design2`.
- **Benchling CSV Export** (`--export benchling`):
  - Generate Benchling-compatible CSV format for direct import.
  - Columns: Name, Bases, Notes (with Tm and GC info).
- **Batch Run Command** (`primerlab batch-run`):
  - Execute multiple config files in one command.
  - **NEW: Multi-FASTA mode** (`--fasta genes.fasta --config params.yaml`)
  - Consolidated summary with success/fail stats.
  - Combined Excel output (`batch_summary.xlsx`).
  - Supports `--continue-on-error` for fault tolerance.
- **Batch Mode Summary** (`core/batch_summary.py`):
  - Consolidated summary report for multi-sequence runs.
  - Combined Excel output with summary sheet.
  - CLI formatted summary output.
- **JSON Schema for Config**:
  - `config/schema.json` for YAML validation.
  - VSCode autocomplete support via `.vscode/settings.json`.
- **Structured Error Details**:
  - `ToolExecutionError` now includes detailed failure info.
  - Enables smart suggestion generation.
- **GC Profile Plot** (`primerlab plot`):
  - Professional visualization of GC content across amplicon.
  - Light/dark mode themes (`--theme light|dark`).
  - Primer position highlighting.
  - Configurable sliding window (`--window 20`).
- **Primer Database** (`primerlab history`):
  - SQLite-based storage for design history.
  - Auto-save on successful workflow runs.
  - Subcommands: `list`, `show`, `export`, `stats`, `delete`.
  - Search by gene name, workflow type.
  - Export history to CSV.
- **Region Masking** (`--mask` flag):
  - Auto-detect lowercase (RepeatMasker) and N-masked regions.
  - Modes: `auto`, `lowercase`, `n`, `none`.
  - Regions excluded from primer placement.
  - BED file support for custom exclusion zones.

### Improved

- Better error handling for design failures with specific relaxation tips.

## [0.1.4] - 2025-12-10

### Added

- **Primer Quality Score (0-100)**:
  - Combined scoring from Primer3, ViennaRNA, and Sequence QC.
  - Mode-specific penalties (strict, standard, relaxed).
  - Categories: Excellent (85-100), Good (70-84), Fair (50-69), Poor (0-49).
  - Scientific backing from Benchling 2024, IDT, DeGenPrime guidelines.
- **"Why This Primer?" Rationale**:
  - Explains why the selected primer was chosen.
  - Shows rejected candidates count and top rejection reasons.
  - Included in Markdown and HTML reports.
- **Audit Log (audit.json)**:
  - Captures all parameters, config hash, sequence hash.
  - Records quality score and candidates summary.
  - Enables reproducibility and troubleshooting.
- **Excel Export (.xlsx)**:
  - Formatted primer table with color-coded Tm/GC values.
  - QC Summary sheet with quality score.
  - Requires openpyxl dependency.
- **IDT Bulk Ordering Template**:
  - Plate layout format (A1, A2, etc.).
  - Ready for IDT bulk upload.
- **HTML Report Generator**:
  - Standalone HTML with embedded CSS.
  - Quality score banner with color coding.
  - "Why This Primer?" section.
  - Copy-to-clipboard functionality.
- **Target Region Specification**:
  - `parameters.target_region.start` and `length` in config.
  - `parameters.excluded_regions` for avoiding specific areas.
  - Integrates with Primer3 SEQUENCE_TARGET.
- **New Export Formats**:
  - `--export xlsx` for Excel output.
  - `--export html` for HTML report.
  - `--export idt_bulk` for plate-ordered Excel.

### Improved

- Scoring documentation with scientific references.
- Report now includes Quality Score in Summary Statistics.

### Dependencies

- Added `openpyxl>=3.1.0` for Excel export.

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
