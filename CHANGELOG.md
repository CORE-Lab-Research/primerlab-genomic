# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
