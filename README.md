# 🧬 PrimerLab Genomic

A modular bioinformatics framework for automated **primer and probe design**, built with clean architecture and reproducible workflows.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)
[![Tests](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml/badge.svg)](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml)
[![Status](https://img.shields.io/badge/status-v0.1.6-blue.svg)](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.1.6)

> 🔰 **Latest Release**: [**v0.1.6 - Stabilization & Testing**](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.1.6) 🎉

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

#### v0.1.6 New Features

* **Sequence Analysis** (`primerlab stats`): Quick sequence stats before design
* **IUPAC Support**: Ambiguous codes (R,Y,W,S,K,M,B,D,H,V) auto-converted to N
* **RNA Detection**: Uracil (U) auto-converted to Thymine (T)
* **Quiet Mode** (`--quiet`): Suppress warnings for scripted pipelines
* **Version Check**: `primerlab health` notifies if newer release available

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
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.1.6
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

Full documentation is available in the [`Docs/`](Docs/) directory:

* **[Project Overview](Docs/High-Level%20Documentation/project-overview.md)** — Vision, scope, and future development
* **[Development Rules](Docs/Development%20Rules/rules-development.md)** — Architecture constraints and coding standards
* **[System Architecture](Docs/Manual%20Plan/)** — Workflow structure, data flow, and roadmap
* **[WSL Quickstart](Docs/Guide/wsl_quickstart.md)** — Setup guide for Windows environments
* **[CHANGELOG](CHANGELOG.md)** — Version history and release notes

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
│   ├── core/             # Reusable utilities (sequence, QC, tools)
│   │   ├── tools/        # Primer3, ViennaRNA wrappers
│   │   └── models/       # Data models and schema
│   ├── workflows/        # Workflow modules
│   │   ├── pcr/          # PCR workflow implementation
│   │   └── qpcr/         # qPCR workflow implementation
│   ├── api/              # Public API
│   └── config/           # Default configurations
├── tests/                # Automated test suite
├── Docs/                 # High-level documentation
└── examples/             # Example configurations
```

---

## 📌 Development Status

### ✅ **v0.1.6** (Current)

The current release includes all v0.1.5 features plus:

* **Sequence Analysis** (`primerlab stats`):
  * Quick sequence stats before design
  * IUPAC code and RNA detection
  * JSON output for pipelines
* **IUPAC & RNA Support**:
  * Auto-convert ambiguous codes to N
  * Auto-convert RNA (U) to DNA (T)
* **Quiet Mode** (`--quiet`):
  * Suppress warnings for scripted pipelines
* **Version Check** in `primerlab health`
* **196 Tests** - Comprehensive test coverage

### v0.1.5 Features

* **Batch Run Command** (`primerlab batch-run`)
* **GC Profile Visualization** (`primerlab plot`)
* **Primer Database** (`primerlab history`)
* **Region Masking** (`--mask` flag)
* **Primer Comparison** (`primerlab compare`)
* **Auto Parameter Suggestion**

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

See: 📄 [`rules-development.md`](Docs/Development%20Rules/rules-development.md)

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
