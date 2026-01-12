# PrimerLab Documentation

**PrimerLab** is a modular bioinformatics framework for automated primer and probe design.

## Quick Links

* **[Quick Start](guides/quickstart.md)**: Design your first primers in 5 minutes.
* **[Guides](guides/index.md)**: Step-by-step tutorials for PCR, qPCR, and more.
* **[Reference](reference/cli.md)**: CLI commands, API docs, and configuration.
* **[Concepts](concepts/index.md)**: Learn about scoring, algorithms, and quality control.

---

## Installation

```bash
pip install primerlab-genomic
```

Verify installation:

```bash
primerlab --version
primerlab health
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **PCR Design** | Standard primer design with quality control |
| **qPCR Design** | TaqMan and SYBR Green assay design |
| **In-silico PCR** | Virtual amplification validation |
| **Off-target Check** | BLAST-based specificity analysis |
| **Batch Processing** | Multi-sequence design |
| **Species Specificity** | Cross-reactivity testing |

---

## Quick Example

```bash
# Create configuration
cat > my_config.yaml << 'EOF'
input:
  sequence_path: ./gene.fasta
parameters:
  tm:
    opt: 60.0
  product_size:
    min: 150
    max: 300
EOF

# Design primers
primerlab run pcr --config my_config.yaml
```

---

## Architecture

PrimerLab uses a three-tier design:

```mermaid
graph LR
    CLI[CLI] --> Workflow[Workflows]
    API[Python API] --> Workflow
    Workflow --> Core[Core Utilities]
    Core --> P3[Primer3]
    Core --> BLAST[BLAST+]
```

Learn more: [System Architecture](concepts/architecture.md)

---

## Version

Current version: **v1.0.1**

See [Changelog](changelog.md) for version history.

---

## Links

* [GitHub Repository](https://github.com/engkinandatama/primerlab-genomic)
* [PyPI Package](https://pypi.org/project/primerlab-genomic/)
* [DeepWiki Docs](https://deepwiki.com/engkinandatama/primerlab-genomic)
