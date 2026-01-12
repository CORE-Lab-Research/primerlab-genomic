# Architecture

PrimerLab uses a 3-layer architecture for modularity and maintainability.

## Overview

```
CLI Layer → Workflow Layer → Core Layer
```

## Layers

### CLI Layer (`primerlab/cli/`)

- Parses command-line arguments
- Loads configuration
- Orchestrates workflows
- Handles output

### Workflow Layer (`primerlab/workflows/`)

- PCR workflow (`workflows/pcr/`)
- qPCR workflow (`workflows/qpcr/`)
- Step-by-step execution
- Workflow-specific QC

### Core Layer (`primerlab/core/`)

- Shared utilities
- Primer3 wrapper
- BLAST integration
- Thermodynamic calculations
- Data models

## Import Rules

```
✅ Allowed:
cli → workflows → core

❌ Not Allowed:
core → workflows
workflows → CLI
```

## Folder Structure

```
primerlab/
├── api/          # Public API
├── cli/          # Command-line interface
├── core/         # Shared utilities
│   ├── insilico/ # In-silico PCR
│   ├── offtarget/# BLAST integration
│   ├── report/   # Report generation
│   ├── tools/    # External wrappers
│   └── models/   # Data models
└── workflows/    # Workflow modules
    ├── pcr/
    └── qpcr/
```

## For Developers

See `.dev/High-Level Documentation/architecture.md` for detailed architecture documentation.
