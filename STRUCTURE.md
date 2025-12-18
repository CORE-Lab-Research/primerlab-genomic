# PrimerLab Project Structure

```
primerlab-genomic/
├── primerlab/                      # Main package
│   ├── __init__.py                 # Package version (0.2.0)
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
│   │   └── tools/                  # External tool wrappers
│   │       ├── __init__.py
│   │       ├── primer3_wrapper.py  # Primer3 interface
│   │       └── vienna_wrapper.py   # ViennaRNA interface
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
├── tests/                          # Test suite (228+ tests)
│   ├── test_insilico.py            # v0.2.0: In-silico tests
│   ├── test_cli_insilico.py        # CLI integration tests
│   ├── test_cli.py
│   ├── test_pcr.py
│   ├── test_qpcr.py
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

*Last updated: 2025-12-18 (v0.2.0)*
