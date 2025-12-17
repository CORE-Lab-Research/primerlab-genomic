# 🤖 Agent Session Log

Format: `[TIMESTAMP] [TYPE] message`
Types: `INFO`, `CHANGE`, `FIX`, `TODO`, `WARN`, `ERR`

---

## Quick Reference

- **Current Version**: v0.1.4 (CHANGELOG) / CLI v0.1.5
- **v0.1.5 Pending**: Auto Suggestion, Primer Comparison, Benchling Export
- **Dev Environment**: Requires WSL (primer3-py doesn't work on Windows native)

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

# ===== v0.1.5 Development (Current) =====
[2025-12-xx] CHANGE  Added FASTA file input support (sequence.py)
[2025-12-xx] CHANGE  Added primer naming convention ({gene}_F1, {gene}_R1)
[2025-12-xx] CHANGE  Added amplicon sequence extraction
[2025-12-xx] CHANGE  Added CLI validate command
[2025-12-xx] CHANGE  Added CLI preset list/show commands
[2025-12-xx] TODO    Auto Parameter Suggestion - not implemented
[2025-12-xx] TODO    Primer Comparison Tool - not implemented
[2025-12-xx] TODO    Benchling CSV Export - not implemented
[2025-12-xx] INFO    Interactive CLI Wizard moved to v1.0 Future Plan

# ===== Session 2025-12-17 (Agent Review) =====
[2025-12-17 20:46] INFO    Session start - Conv ID: 3e04b361
[2025-12-17 20:47] INFO    Read artifacts from prev session (f57f96b3)
[2025-12-17 20:50] INFO    Read all Docs/Development Rules and High-Level Documentation
[2025-12-17 20:55] CHANGE  Created SESSION_LOG.md for cross-session continuity
[2025-12-17 20:55] CHANGE  Updated ai-helper-rules.md - added Rule 1.6 (session log mandatory)
[2025-12-17 21:01] INFO    Started comprehensive project review
[2025-12-17 21:05] INFO    Reviewed: CLI(513 lines), PCR(219), qPCR(133), Primer3(188), Vienna(147)
[2025-12-17 21:07] WARN    pytest fails on Windows native - primer3-py requires WSL
[2025-12-17 21:08] INFO    No critical bugs found - architecture is solid
[2025-12-17 21:12] CHANGE  Simplified SESSION_LOG.md to debug-log format
[2025-12-17 21:13] INFO    Wrote historical log entries from CHANGELOG

# ===== v0.1.5 Priority 4: Smart Features =====
[2025-12-17 21:17] INFO    Started v0.1.5 Priority 4 implementation
[2025-12-17 21:18] CHANGE  Created core/suggestion.py (285 lines) - Auto Parameter Suggestion
[2025-12-17 21:19] CHANGE  Updated primer3_wrapper.py - added structured error details
[2025-12-17 21:20] CHANGE  Created core/comparison.py (350 lines) - Primer Comparison Tool
[2025-12-17 21:21] CHANGE  Updated cli/main.py - added compare command + suggestion integration
[2025-12-17 21:22] CHANGE  Created tests/test_suggestion.py (145 lines)
[2025-12-17 21:27] CHANGE  Created tests/test_comparison.py (200 lines)
[2025-12-17 21:44] INFO    Git commit 8813829 - feat(v0.1.5): Add Auto Parameter Suggestion and Primer Comparison Tool
[2025-12-17 21:51] INFO    All 29 tests passed (test_suggestion + test_comparison)

# ===== v0.1.5 Priority 5: Export & Integration =====
[2025-12-17 21:52] INFO    Started v0.1.5 Priority 5 implementation
[2025-12-17 21:53] CHANGE  Added save_benchling_csv() to output.py
[2025-12-17 21:53] CHANGE  Updated cli/main.py - added benchling export format
[2025-12-17 21:54] CHANGE  Created core/batch_summary.py (280 lines) - batch summary reports
[2025-12-17 21:55] CHANGE  Created config/schema.json - JSON Schema for YAML validation
[2025-12-17 21:55] CHANGE  Created .vscode/settings.json - VSCode autocomplete
[2025-12-17 21:56] CHANGE  Created tests/test_batch_summary.py (110 lines)
```

---

## Context Notes (Update when major state changes)

Last updated: 2025-12-17

- v0.1-v0.4 milestones: COMPLETE
- v0.1.5: Partial (FASTA done, Auto-suggestion pending)
- Interactive CLI Wizard: Moved to v1.0 Future Plan
- Next targets: v0.1.5 pending features OR v0.2.0 CRISPR
