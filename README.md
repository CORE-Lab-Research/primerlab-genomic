# 🧬 PrimerLab Genomic

A modular bioinformatics framework for automated **primer and probe design**, built with clean architecture and reproducible workflows.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)
[![Tests](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml/badge.svg)](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml)
[![Status](https://img.shields.io/badge/status-v0.2.5-blue.svg)](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.2.5)

> 🔰 **Latest Release**: [**v0.2.5 - In-silico PCR Simulation**](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.2.5) 🎉

---

## 📋 Overview

**PrimerLab Genomic** is a Python-based toolkit for automated primer and probe design in molecular biology workflows.
It provides a structured and reproducible framework for:

* **PCR** — Standard primer design with quality control
* **qPCR** — Probe design with thermodynamic checks
* **(Future)** CRISPR guides, multiplex PCR, and specialized workflows

PrimerLab focuses on **deterministic, transparent bioinformatics**, following strict modularity and best practices.

### 🔑 Key Features

* **End-to-End Workflow**: Sequence input → Primer/Probe design → QC → Report
* **Thermodynamic Validation**: Secondary structure prediction via ViennaRNA
* **QC Framework**: Hairpins, dimers, GC%, Tm ranges, amplicon checks
* **qPCR Support**: TaqMan-style probe design with efficiency estimation
* **Safe Execution**: Timeout protection for complex sequences
* **Structured Output**: JSON + Markdown reports with interpretable metrics

#### v0.2.5 New Features

* **In-silico PCR** (`primerlab insilico`): Validate primers against template
* **IUPAC Support**: Degenerate bases (R, Y, S, W, K, M, B, D, H, V, N)
* **Circular Template**: `--circular` flag for plasmid/bacterial DNA
* **Integrated Validation**: `--validate` flag for auto in-silico after design
* **Primer-Dimer Check**: Fwd↔Rev complementarity detection
* **Extension Time**: Estimated PCR extension time (1 min/kb)
* **Markdown Reports**: Human-readable in-silico reports

---

## 🚀 Quick Start

### Installation

#### Option 1: For Developers (Source)

```bash
# Clone the repository
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic

# Create virtual environment (recommended)
python3 -m venv ~/primerlab_venv
source ~/primerlab_venv/bin/activate  # Linux/WSL
# or
# .\primerlab_venv\Scripts\activate   # Windows PowerShell

# Install dependencies & package in editable mode
pip install -e .
```

#### Option 2: For End Users (From GitHub Release)

```bash
# Install directly from GitHub (latest release)
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.2.5
```

Once installed, verify the installation:

```bash
primerlab --version
```

---

## 🔧 Usage

### Command-Line Interface (CLI)

**PCR Workflow:**

```bash
primerlab run pcr --config test_pcr.yaml
```

**qPCR Workflow:**

```bash
primerlab run qpcr --config test_qpcr.yaml
```

**Sequence Stats (v0.1.6):**

```bash
# Check sequence before design
primerlab stats input.fasta

# JSON output for pipelines
primerlab stats input.fasta --json
```

**Quiet Mode (v0.1.6):**

```bash
# Suppress warnings for scripted pipelines
primerlab run pcr --config test_pcr.yaml --quiet
```

**In-silico PCR Simulation (v0.2.0):**

```bash
# Validate primers against template
primerlab insilico -p primers.json -t template.fasta

# With custom output directory
primerlab insilico -p primers.json -t template.fasta -o results/

# JSON output for pipelines
primerlab insilico -p primers.json -t template.fasta --json
```

Example `primers.json`:

```json
{
  "forward": "ATGGTGAGCAAGGGCGAGGAG",
  "reverse": "TTACTTGTACAGCTCGTCCATGCC"
}
```

### Programmatic API (Python)

For integration into your own Python scripts:

```python
from primerlab.api.public import design_pcr_primers, design_qpcr_assays

# PCR primer design
sequence = "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT..."
result = design_pcr_primers(sequence)

print(f"Forward: {result.primers['forward'].sequence}")
print(f"Reverse: {result.primers['reverse'].sequence}")
print(f"Amplicon: {result.amplicons[0].length} bp")

# qPCR assay design (with custom parameters)
config = {
    "parameters": {
        "product_size_range": [[70, 200]],
        "probe": {"tm": {"min": 68.0, "opt": 70.0, "max": 72.0}}
    }
}
result = design_qpcr_assays(sequence, config)

print(f"Probe: {result.primers['probe'].sequence}")
print(f"Efficiency: {result.efficiency}%")
```

---

## 📖 Documentation

Full documentation is available in the [`docs/`](docs/) directory:

* **[CLI Reference](docs/cli/README.md)** — All available commands
* **[In-silico PCR](docs/cli/insilico.md)** — Primer validation (v0.2.0)
* **[WSL Quickstart](.dev/Guide/wsl_quickstart.md)** — Setup guide for Windows
* **[CHANGELOG](CHANGELOG.md)** — Version history and release notes
* **[STRUCTURE](STRUCTURE.md)** — Project architecture

---

## 🧪 Example Configurations

### PCR Configuration

```yaml
workflow: pcr

input:
  sequence: "ATGAGTAAAGGAGAAGAACTTTTCACTGGAGT..."  # Or use sequence_path: "input.fasta"

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size: {min: 200, opt: 400, max: 600}  # v0.1.1: Simplified syntax

output:
  directory: "output_pcr"
```

### qPCR Configuration (TaqMan - Default)

```yaml
workflow: qpcr
# mode: taqman (default - includes probe design)

input:
  sequence: "ATGGGGAAGGTGAAGGTCGGAGT..."

parameters:
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 55.0, opt: 60.0, max: 65.0}
  
  probe:
    size: {min: 18, opt: 24, max: 30}
    tm: {min: 68.0, opt: 70.0, max: 72.0}

output:
  directory: "output_qpcr"
```

### qPCR Configuration (SYBR Green)

```yaml
workflow: qpcr

parameters:
  mode: sybr  # v0.1.1: Disables probe design automatically
  
  primer_size: {min: 18, opt: 20, max: 24}
  tm: {min: 58.0, opt: 60.0, max: 62.0}
  product_size: {min: 70, opt: 100, max: 150}

output:
  directory: "output_qpcr_sybr"
```

---

## 📊 Output Overview

PrimerLab generates a structured report containing:

* **Primer & Probe Details** — Sequences, GC%, Tm, positions
* **qPCR Metrics** — Estimated amplification efficiency
* **Amplicon Properties** — Length, GC%, suitability
* **QC Checks** — Dimers, hairpins, Tm balance
* **Warnings** — Optimization suggestions

Run a workflow to generate your own report!

---

## 🏗️ Project Structure

```text
primerlab-genomic/
├── primerlab/
│   ├── cli/              # Command-line interface
│   ├── core/             # Reusable utilities
│   │   ├── insilico/     # In-silico PCR simulation (v0.2.0)
│   │   └── tools/        # Primer3, ViennaRNA wrappers
│   ├── workflows/        # Workflow modules
│   │   ├── pcr/          # PCR workflow
│   │   └── qpcr/         # qPCR workflow
│   ├── api/              # Public API
│   └── config/           # Default configurations
├── tests/                # 228+ automated tests
├── docs/                 # User documentation
├── examples/             # Example files
│   └── insilico/         # In-silico PCR examples
└── .dev/                 # Internal dev docs
```

---

## 📌 Development Status

### ✅ **v0.2.5** (Current)

* **In-silico PCR Simulation** (`primerlab insilico`):
  * Virtual PCR engine with binding site analysis
  * IUPAC degenerate base support
  * Circular template support (`--circular`)
  * Primer-dimer detection
  * Extension time estimation
* **Integrated Validation** (`--validate`):
  * Auto in-silico after primer design
* **228 Tests** - Comprehensive test coverage

### v0.1.6 Features

* Sequence Analysis (`primerlab stats`)
* IUPAC & RNA auto-conversion
* Quiet mode (`--quiet`)
* Version check in `primerlab health`

### v0.1.5 Features

* Batch Run Command (`primerlab batch-run`)
* GC Profile Visualization (`primerlab plot`)
* Primer Database (`primerlab history`)
* Region Masking (`--mask` flag)
* Auto Parameter Suggestion

---

## 🛠️ Requirements

* **Python 3.10+**
* **Primer3** (`primer3-py`)
* **ViennaRNA** for secondary structure prediction
* **WSL recommended for Windows users**

---

## 🤝 Contributing

PrimerLab follows strict architecture guidelines:

* No cross-layer imports
* Consistent naming conventions
* Explicit error handling
* Deterministic, reproducible outputs

See: 📄 [`rules-development.md`](docs/Development%20Rules/rules-development.md)

---

## 📄 License

This project is licensed under the **BSD 3-Clause License**.
See the [LICENSE](LICENSE) file for details.

© 2025–present — **Engki Nandatama**

---

## 🙏 Acknowledgments

* **Primer3** — Primary primer design engine
* **ViennaRNA** — Thermodynamic folding & secondary structure analysis

---

## 📬 Contact

For issues, suggestions, or contributions:

➡️ **[Open an issue on GitHub](https://github.com/engkinandatama/primerlab-genomic/issues)**
