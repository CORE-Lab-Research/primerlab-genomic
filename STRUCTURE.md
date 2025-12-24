# PrimerLab Project Structure

```
primerlab-genomic/
├── primerlab/                      # Main package
│   ├── __init__.py                 # Package version (0.3.4)
│   │
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                 # CLI entry point
│   │
│   ├── api/                        # Public API
│   │   ├── __init__.py
│   │   └── public.py               # design_pcr_primers(), design_qpcr_assays()
│   │
│   ├── core/                       # Core utilities
│   │   ├── __init__.py
│   │   ├── config_loader.py        # YAML config loading & validation
│   │   ├── database.py             # Primer design history (SQLite)
│   │   ├── exceptions.py           # Custom exceptions & error codes
│   │   ├── logger.py               # Logging system
│   │   ├── masking.py              # Region masking (BED)
│   │   ├── models.py               # Data models (Primer, Amplicon, etc.)
│   │   ├── output.py               # Output manager (JSON, reports)
│   │   ├── sequence.py             # Sequence loading & validation
│   │   ├── visualization.py        # GC profile plots
│   │   │
│   │   ├── insilico/               # v0.2.0: In-silico PCR module
│   │   │   ├── __init__.py         # run_insilico_pcr()
│   │   │   ├── engine.py           # Virtual PCR engine
│   │   │   └── binding.py          # Binding site analysis
│   │   │
│   │   ├── offtarget/              # v0.3.0: Off-target detection
│   │   │   ├── __init__.py
│   │   │   └── variant_check.py    # Primer-SNP overlap detection
│   │   │
│   │   ├── report/                 # v0.3.3: Report generation
│   │   │   ├── __init__.py         # Package exports
│   │   │   ├── models.py           # PrimerReport, DesignSummary
│   │   │   ├── generator.py        # Markdown/JSON generator
│   │   │   ├── alignment_view.py   # ASCII alignment visualization
│   │   │   ├── html_export.py      # HTML report (dark mode)
│   │   │   └── json_export.py      # JSON report
│   │   │
│   │   ├── tools/                  # External tool wrappers
│   │   │   ├── __init__.py
│   │   │   ├── primer3_wrapper.py  # Primer3 interface
│   │   │   ├── vienna_wrapper.py   # ViennaRNA interface
│   │   │   ├── blast_cache.py      # v0.3.2: SQLite BLAST cache
│   │   │   ├── parallel_blast.py   # v0.3.2: Multi-threaded BLAST
│   │   │   ├── ncbi_blast.py       # v0.3.2: NCBI Web BLAST
│   │   │   └── vcf_parser.py       # v0.3.1: VCF/variant parser
│   │   │
│   │   └── models/                 # Data models
│   │       ├── blast.py            # BlastResult, BlastHit
│   │       └── variant.py          # Variant, VariantOverlap
│   │
│   ├── workflows/                  # Workflow modules
│   │   ├── __init__.py
│   │   │
│   │   ├── pcr/                    # PCR workflow
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py         # Main PCR workflow
│   │   │   ├── qc.py               # PCR QC logic
│   │   │   └── report.py           # PCR report generator
│   │   │
│   │   └── qpcr/                   # qPCR workflow
│   │       ├── __init__.py
│   │       ├── workflow.py         # Main qPCR workflow
│   │       ├── design.py           # Primer/probe parsing
│   │       ├── qc.py               # qPCR QC + efficiency
│   │       ├── report.py           # qPCR report generator
│   │       └── progress.py         # Progress tracking
│   │
│   └── config/                     # Default configurations
│       ├── presets/                # Built-in presets
│       ├── pcr_default.yaml
│       └── qpcr_default.yaml
│
├── tests/                          # Test suite (320+ tests)
│   ├── test_report.py              # v0.3.3: Report tests
│   ├── test_blast_cache.py         # v0.3.2: Cache tests
│   ├── test_parallel_blast.py      # v0.3.2: Parallel BLAST tests
│   ├── test_insilico.py            # v0.2.0: In-silico tests
│   ├── test_cli.py
│   └── ...
│
├── examples/                       # Example files
│   ├── insilico/                   # v0.2.0: In-silico examples
│   │   ├── primers.json
│   │   └── template.fasta
│   ├── multi_sequences.fasta
│   └── ...
│
├── docs/                           # User documentation
│   ├── cli/                        # CLI reference
│   │   ├── README.md
│   │   ├── insilico.md             # v0.2.0
│   │   ├── run.md
│   │   └── ...
│   └── ...
│
├── .dev/                           # Internal dev docs
│   └── AI Helper Files/
│       └── SESSION_LOG.md
│
├── .github/                        # CI/CD
│   └── workflows/
│       └── test.yml
│
├── CHANGELOG.md
├── README.md
├── RELEASE_NOTES.md                # v0.2.0
├── STRUCTURE.md                    # This file
├── pyproject.toml
└── LICENSE

```

## Architecture

```

┌─────────────┐
│     CLI     │  primerlab run/insilico/stats/...
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Workflows  │  PCR, qPCR (modular, isolated)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    Core     │  Tools, Models, Utilities, In-silico
└─────────────┘

```

## Module Summary

| Module | Purpose |
|--------|---------|
| `cli/` | Command-line interface |
| `api/` | Public Python API |
| `core/` | Shared utilities |
| `core/insilico/` | In-silico PCR simulation (v0.2.0) |
| `core/tools/` | Primer3, ViennaRNA wrappers |
| `workflows/pcr/` | PCR primer design |
| `workflows/qpcr/` | qPCR assay design |

## File Counts

- **Python files**: ~30
- **Tests**: 228+
- **Documentation**: 25+ files

---

*Last updated: 2025-12-20 (v0.2.5)*
