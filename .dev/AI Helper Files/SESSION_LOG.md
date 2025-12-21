# 🤖 Agent Session Log

Format: `[TIMESTAMP] [TYPE] message`
Types: `INFO`, `CHANGE`, `FIX`, `TODO`, `WARN`, `ERR`

---

## Quick Reference

- **Current Version**: v0.3.1 (released)
- **Dev Environment**: Requires WSL (primer3-py doesn't work on Windows native)
- **Test Status**: 302 passed, 0 warnings

---

## Log

```
# ===== v0.1.0 Release (2025-11-27) =====
[2025-11-27] INFO    Project initialized - 3-layer architecture (CLI → Workflows → Core)
[2025-11-27] CHANGE  Created core modules: config_loader.py, logger.py, exceptions.py
[2025-11-27] CHANGE  Created PCR workflow: workflow.py, qc.py, report.py
[2025-11-27] CHANGE  Created qPCR workflow with TaqMan probe support
[2025-11-27] CHANGE  Created Primer3 wrapper with primer3-py bindings
[2025-11-27] CHANGE  Created ViennaRNA wrapper for secondary structure QC
[2025-11-27] CHANGE  Created API layer: api/__init__.py, api/public.py
[2025-11-27] CHANGE  Created test suite: test_pcr.py, test_qpcr.py, test_api.py
[2025-11-27] FIX     Fixed reverse primer coordinate calculation (3' vs 5' index)
[2025-11-27] FIX     Fixed QC silent pass when ViennaRNA missing

# ===== v0.1.1 Patch (2025-11-30) =====
[2025-11-30] CHANGE  Added product_size simplified syntax (min/opt/max)
[2025-11-30] CHANGE  Added preset configuration support (long_range, standard_pcr)
[2025-11-30] CHANGE  Added qPCR mode parameter (sybr/taqman)
[2025-11-30] FIX     Fixed SetuptoolsDeprecationWarning in pyproject.toml

# ===== v0.1.2 Release (2025-12-07) =====
[2025-12-07] CHANGE  Added 4 example configs (pcr_standard, pcr_long_range, qpcr_taqman, qpcr_sybr)
[2025-12-07] CHANGE  Added CSV export for primers
[2025-12-07] CHANGE  Added vendor ordering formats (IDT, Sigma, Thermo)
[2025-12-07] CHANGE  Added --dry-run CLI flag
[2025-12-07] CHANGE  Added batch-generate command
[2025-12-07] FIX     Added minimum sequence length validation (50bp)
[2025-12-07] FIX     Added detailed Primer3 failure reasons

# ===== v0.1.3 Release (2025-12-08) =====
[2025-12-08] CHANGE  Added multi-candidate reranking engine (core/reranking.py)
[2025-12-08] CHANGE  Added GC clamp check and poly-X detection (sequence_qc.py)
[2025-12-08] CHANGE  Added presets: dna_barcoding, rt_pcr, long_range
[2025-12-08] CHANGE  Added CLI commands: init, health
[2025-12-08] CHANGE  Added --export flag for vendor format selection
[2025-12-08] CHANGE  Added Rich colorized output and tqdm progress bars
[2025-12-08] CHANGE  Added advanced.seed for reproducibility
[2025-12-08] CHANGE  Added Docs/Guide: troubleshooting.md, qc-metrics.md, reranking-algorithm.md

# ===== v0.1.4 Release (2025-12-10) =====
[2025-12-10] CHANGE  Added Primer Quality Score (0-100) in scoring.py
[2025-12-10] CHANGE  Added "Why This Primer?" rationale in rationale.py
[2025-12-10] CHANGE  Added audit.json logging in audit.py
[2025-12-10] CHANGE  Added Excel export (.xlsx) with openpyxl
[2025-12-10] CHANGE  Added IDT bulk ordering template
[2025-12-10] CHANGE  Added HTML report generator (html_report.py)
[2025-12-10] CHANGE  Added target_region and excluded_regions in Primer3 wrapper
[2025-12-10] CHANGE  Added --export xlsx, html, idt_bulk options

# ===== v0.1.5 Release (2025-12-17) =====
[2025-12-17] CHANGE  Added Auto Parameter Suggestion (core/suggestion.py)
[2025-12-17] CHANGE  Added Primer Comparison Tool (core/comparison.py, CLI compare)
[2025-12-17] CHANGE  Added Benchling CSV Export (--export benchling)
[2025-12-17] CHANGE  Added Batch Run Command (primerlab batch-run)
[2025-12-17] CHANGE  Added GC Profile Plot (primerlab plot, requires matplotlib)
[2025-12-17] CHANGE  Added Primer Database (primerlab history, SQLite)
[2025-12-17] CHANGE  Added Region Masking (--mask auto/lowercase/n)
[2025-12-17] CHANGE  Added JSON Schema for config validation

# ===== v0.1.6 Development (2025-12-17 - 2025-12-18) =====
[2025-12-17 22:48] INFO    Session start - v0.1.6 Stabilization & Testing
[2025-12-17 23:00] CHANGE  Created test fixtures (multi_sequences.fasta, masked_sequence.fasta, etc.)
[2025-12-17 23:15] CHANGE  Created test_visualization.py (13 tests)
[2025-12-17 23:20] CHANGE  Created test_database.py (9 tests)
[2025-12-17 23:25] CHANGE  Created test_masking.py (9 tests)
[2025-12-17 23:30] CHANGE  Added matplotlib to required dependencies
[2025-12-17 23:45] CHANGE  Created test_integration.py (10 E2E tests)
[2025-12-18 00:00] CHANGE  Added IUPAC ambiguous codes handling (R,Y,W,S,K,M,B,D,H,V → N)
[2025-12-18 00:05] CHANGE  Added RNA sequence detection (U → T conversion)
[2025-12-18 00:15] CHANGE  Created test_sequence.py (14 tests)
[2025-12-18 00:30] CHANGE  Added primerlab stats command
[2025-12-18 00:35] CHANGE  Added version check in primerlab health
[2025-12-18 00:45] CHANGE  Added --quiet flag for run command
[2025-12-18 00:50] CHANGE  Created test_stats.py (8 tests)
[2025-12-18 01:00] FIX     Fixed datetime.utcnow() deprecation warning
[2025-12-18 01:45] CHANGE  Bumped version to 0.1.6
[2025-12-18 01:50] CHANGE  Updated CHANGELOG.md with v0.1.6 entries
[2025-12-18 02:00] CHANGE  Updated README.md with v0.1.6 features
[2025-12-18 02:10] CHANGE  Created comprehensive docs (20 files in Docs/)
[2025-12-18 02:20] CHANGE  Reorganized docs - moved internal to .dev/
[2025-12-18 02:25] INFO    Total: 196 tests passing, 0 warnings

# ===== v0.2.0 Release (2025-12-18) =====
[2025-12-18 03:00] INFO    Started v0.2.0 - In-silico PCR Simulation
[2025-12-18 04:30] CHANGE  Created core/insilico/engine.py (Virtual PCR Engine)
[2025-12-18 05:00] CHANGE  Created core/insilico/binding.py (Binding Site Analysis)
[2025-12-18 05:30] CHANGE  Created tests/test_insilico.py (24 unit tests)
[2025-12-18 06:00] CHANGE  Added primerlab insilico CLI command
[2025-12-18 06:30] CHANGE  Implemented multi-product prediction with likelihood scoring
[2025-12-18 06:45] CHANGE  Enhanced YAML error handling (line numbers, hints)
[2025-12-18 07:00] CHANGE  Added database resilience (integrity check, auto-backup)
[2025-12-18 11:30] CHANGE  Added predicted_amplicons.fasta output
[2025-12-18 11:45] CHANGE  Added alignment visualization in CLI
[2025-12-18 12:00] CHANGE  Created examples/insilico/ (primers.json, template.fasta)
[2025-12-18 12:30] CHANGE  Created tests/test_cli_insilico.py (CLI integration tests)
[2025-12-18 13:00] FIX     Fixed --json flag to suppress logger for clean output
[2025-12-18 13:15] CHANGE  Updated .gitignore and cleaned output files
[2025-12-18 13:20] CHANGE  Created docs/cli/insilico.md
[2025-12-18 13:25] INFO    Bumped version to 0.2.0, 228 tests passing

# ===== v0.2.1 - v0.2.5 Releases (2025-12-18 - 2025-12-20) =====
[2025-12-18] CHANGE  v0.2.1: Degenerate primer support, semantic matching
[2025-12-19] CHANGE  v0.2.2: Improved binding scoring algorithms
[2025-12-19] CHANGE  v0.2.3: Auto-validate after design (--validate flag)
[2025-12-20] CHANGE  v0.2.4: Circular template support (--circular flag)
[2025-12-20] CHANGE  v0.2.5: Primer-dimer check, extension time estimation

# ===== v0.3.0 Release (2025-12-21) =====
[2025-12-21 00:00] INFO    Started v0.3.0 - BLAST Integration
[2025-12-21 10:00] CHANGE  Created core/tools/blast_wrapper.py (BLAST+ wrapper)
[2025-12-21 10:30] CHANGE  Created core/tools/align_fallback.py (Biopython aligner)
[2025-12-21 11:00] CHANGE  Created core/tools/primer_aligner.py (unified interface)
[2025-12-21 11:30] CHANGE  Created core/offtarget/finder.py (off-target detection)
[2025-12-21 12:00] CHANGE  Created core/offtarget/scorer.py (specificity scoring A-F)
[2025-12-21 12:30] CHANGE  Created core/offtarget/report.py (specificity reports)
[2025-12-21 13:00] CHANGE  Added primerlab blast CLI command
[2025-12-21 13:30] CHANGE  Created tests/test_blast_wrapper.py, test_offtarget.py
[2025-12-21 14:00] INFO    Tagged v0.3.0, 285 tests passing

# ===== v0.3.1 Release (2025-12-21) =====
[2025-12-21 12:30] CHANGE  Added --blast, --blast-db flags to run command
[2025-12-21 12:45] CHANGE  Added offtarget: config section (pcr_default.yaml)
[2025-12-21 13:00] CHANGE  Created core/models/variant.py (Variant dataclasses)
[2025-12-21 13:15] CHANGE  Created core/tools/vcf_parser.py (VCF parser)
[2025-12-21 13:30] CHANGE  Created core/tools/bed_parser.py (BED parser)
[2025-12-21 13:45] CHANGE  Created core/offtarget/variant_check.py (SNP detection)
[2025-12-21 14:00] CHANGE  Added check_offtargets() to public API
[2025-12-21 14:10] CHANGE  Added --batch, --db-info, --variants, --maf-threshold flags
[2025-12-21 14:15] CHANGE  Created docs/cli/blast.md
[2025-12-21 14:20] CHANGE  Created examples/workflow_blast_variant.md
[2025-12-21 14:25] CHANGE  Created tests/test_vcf_parser.py, test_api_offtarget.py
[2025-12-21 14:30] INFO    Tagged v0.3.1, 302 tests passing
```

---

## Context Notes (Update when major state changes)

Last updated: 2025-12-21

### Release Status

| Version | Status | Highlights |
|---------|--------|------------|
| v0.1.0 - v0.1.5 | ✅ COMPLETE | Core functionality, smart features |
| v0.1.6 | ✅ RELEASED | Stabilization, testing, docs |
| v0.2.0 - v0.2.5 | ✅ RELEASED | In-silico PCR, degenerate, circular |
| v0.3.0 | ✅ RELEASED | BLAST Integration, off-target detection |
| v0.3.1 | ✅ RELEASED | VCF/BED parsers, variant check, API |

### v0.3.1 Checklist

- [x] --blast and --blast-db flags for run command
- [x] offtarget: config section
- [x] check_offtargets() public API
- [x] VCF parser with gzip/MAF support
- [x] BED parser for region filtering
- [x] Primer-SNP overlap detection
- [x] --batch, --db-info, --variants, --maf-threshold CLI flags
- [x] CLI docs and example workflow
- [x] Tests (302 passed)
- [x] Git tag v0.3.1

### Test Coverage

- **Total Tests**: 302
- **Warnings**: 0
- **New in v0.3.x**: test_blast_wrapper.py, test_offtarget.py, test_vcf_parser.py, test_api_offtarget.py

### Next Steps

1. Push v0.3.1 to GitHub (manual)
2. Start v0.3.2 planning (Polish & UX Improvements)
