# PrimerLab Project Structure

```
primerlab-genomic/
│
├── primerlab/                      # Main package directory
│   ├── __init__.py
│   │
│   ├── cli/                        # Command-line interface
│   │   ├── __init__.py
│   │   └── main.py                 # CLI entry point
│   │
│   ├── core/                       # Core utilities (workflow-agnostic)
│   │   ├── __init__.py
│   │   ├── config_loader.py        # Configuration loader & merger
│   │   ├── exceptions.py           # Custom exceptions & error codes
│   │   ├── logger.py               # Logging system
│   │   ├── models.py               # Data models (Primer, Amplicon, etc.)
│   │   ├── output.py               # Output manager (JSON, reports)
│   │   ├── sequence.py             # Sequence loading & validation
│   │   │
│   │   └── tools/                  # External tool wrappers
│   │       ├── __init__.py
│   │       ├── primer3_wrapper.py  # Primer3 interface (with timeout)
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
│   │       ├── qc.py               # qPCR QC + efficiency estimator
│   │       ├── report.py           # qPCR report generator
│   │       └── progress.py         # Progress tracking steps
│   │
│   └── config/                     # Default configuration files
│       ├── pcr_default.yaml
│       └── qpcr_default.yaml
│
├── Docs/                           # Comprehensive documentation
│   ├── AI Helper Files/            # AI development guides
│   │   ├── ai-helper-overview.md
│   │   └── ...
│   │
│   ├── Blueprint Files/            # System blueprints
│   │   ├── workflow-blueprint.md
│   │   └── ...
│   │
│   ├── Development Rules/          # Coding standards & guidelines
│   │   ├── rules-development.md    # Main development rules
│   │   ├── api-design.md
│   │   ├── coding-style.md
│   │   ├── config-design.md
│   │   ├── data-model.md
│   │   ├── error-codes.md
│   │   ├── exception-handling.md
│   │   ├── logging-progress.md
│   │   ├── naming-convention.md
│   │   └── test-guidelines.md
│   │
│   ├── Guide/                      # User guides
│   │   └── wsl_quickstart.md       # WSL setup guide
│   │
│   ├── High-Level Documentation/   # Architecture & planning
│   │   ├── project-overview.md
│   │   ├── architecture.md
│   │   └── ...
│   │
│   ├── Manual Plan/                # Development roadmap
│   │   ├── short-term.md           # Short-term milestones (v0.1-v0.4)
│   │   ├── mid-term.md
│   │   └── ...
│   │
│   ├── Misc/                       # Miscellaneous docs
│   │   └── ...
│   │
│   └── Project Meta/
│       └── CODE_OF_CONDUCT.md
│
├── tests/                          # (Future) Test suite
│   ├── unit/
│   ├── module/
│   ├── workflow/
│   └── integration/
│
├── test_output/                    # Test output directory (gitignored)
│
├── test_pcr.yaml                   # PCR test configuration
├── test_qpcr.yaml                  # qPCR test configuration
│
├── .gitignore                      # Git ignore rules
├── LICENSE                         # BSD 3-Clause License
├── README.md                       # Project README
├── requirements.txt                # Python dependencies
└── setup.py                        # Package installation script
```

## Key Directories

### `primerlab/` - Main Package
- **cli/** - Command-line interface and argument parsing
- **core/** - Reusable, workflow-agnostic utilities
  - **tools/** - External tool wrappers (Primer3, ViennaRNA)
- **workflows/** - Workflow-specific modules
  - **pcr/** - Standard PCR workflow
  - **qpcr/** - qPCR workflow with probe design
- **config/** - Default YAML configurations

### `Docs/` - Documentation
- **Development Rules/** - Coding standards and guidelines
- **Manual Plan/** - Development roadmap and milestones
- **Guide/** - User setup and usage guides

### Output Directories (gitignored)
- `primerlab_out/` - Default output (production)
- `test_output/` - Test output (development)

## Architecture

```
┌─────────┐
│   CLI   │  Command-line interface
└────┬────┘
     │
     ▼
┌──────────┐
│ Workflows│  PCR, qPCR (modular, isolated)
└────┬─────┘
     │
     ▼
┌──────────┐
│   Core   │  Tools, Models, Utilities (reusable)
└──────────┘
```

**Layer Rules:**
- CLI → Workflows ✅
- CLI → Core ✅
- Workflows → Core ✅
- Core → Workflows ❌
- Workflows → Workflows ❌

## File Counts

- **Total Python files**: ~20
- **Workflow modules**: 2 (PCR, qPCR)
- **Configuration files**: 2 defaults + 2 test configs
- **Documentation files**: 30+

---

*Last updated: 2025-11-27*
