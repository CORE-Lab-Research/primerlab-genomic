# 🧬 PrimerLab Genomic

A modular bioinformatics framework for automated **primer and probe design**, built with clean architecture and reproducible workflows.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-BSD%203--Clause-green.svg)](LICENSE)
[![Tests](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml/badge.svg)](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml)
[![Status](https://img.shields.io/badge/status-v0.6.2-blue.svg)](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.6.2)

> 🔰 **Latest Release**: [**v0.6.2 - Advanced Features**](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v0.6.2) 🎉

---

## 📋 Overview

**PrimerLab Genomic** is a Python-based toolkit for automated primer and probe design in molecular biology workflows.
It provides a structured and reproducible framework for:

* **PCR** — Standard primer design with quality control
* **qPCR** — Probe design with thermodynamic checks
* **Off-target Check** — BLAST-based specificity analysis
* **In-silico PCR** — Virtual PCR simulation and validation

PrimerLab focuses on **deterministic, transparent bioinformatics**, following strict modularity and best practices.

### 🔑 Key Features

* **End-to-End Workflow**: Sequence input → Primer/Probe design → QC → Report
* **Thermodynamic Validation**: Secondary structure prediction via ViennaRNA
* **QC Framework**: Hairpins, dimers, GC%, Tm ranges, amplicon checks
* **qPCR Support**: TaqMan-style probe design with efficiency estimation
* **Safe Execution**: Timeout protection for complex sequences
* **Structured Output**: JSON + Markdown + HTML reports with interpretable metrics

#### 🆕 v0.3.x Features

* **Enhanced Reporting** (v0.3.3): Markdown, HTML, JSON reports with scoring
* **Tm Correction** (v0.3.4): Mismatch-based Tm adjustment
* **3' Stability Warning** (v0.3.4): ΔG threshold checks
* **BLAST Integration** (v0.3.0): Off-target detection with A-F grades
* **In-silico PCR** (v0.2.4): Validate primers against template
* **Parallel BLAST** (v0.3.2): Multi-threaded off-target checking

#### 🆕 v0.4.x Features

* **Primer Compatibility Check** (v0.4.0): Analyze primer sets for cross-dimer formation, Tm uniformity, and GC consistency
* **Excel/IDT Export** (v0.4.0): Export compatibility matrix to Excel, IDT plate format for ordering
* **Amplicon Analysis** (v0.4.1): Secondary structure, GC profile, quality scoring
* **Species Specificity** (v0.4.2): Cross-reactivity check, multi-species template comparison, specificity scoring
* **Tm Gradient Simulation** (v0.4.3): Optimal annealing temperature prediction, temperature sensitivity analysis
* **Batch Species-Check** (v0.4.3): Parallel processing, SQLite caching, CSV batch export

#### 🆕 v0.5.0 Features

* **Probe Binding Simulation** (v0.5.0): TaqMan probe Tm calculation, binding efficiency, position optimization
* **qPCR Amplicon Validation** (v0.5.0): Length/GC validation, secondary structure scoring, efficiency prediction
* **SYBR Melt Curve Prediction** (v0.5.0): Tm prediction, multi-peak detection, quality grading

#### 🆕 v0.6.x Features

* **Allele Discrimination** (v0.6.0): SNP genotyping primer scoring, 3' end position analysis, mismatch Tm calculation
* **RT-qPCR Validation** (v0.6.0): Exon junction detection, gDNA contamination risk assessment
* **Melt Curve Visualization** (v0.6.0): SVG/PNG melt curve plots, multi-peak annotation
* **New CLI Commands** (v0.6.0): `probe-check`, `melt-curve`, `amplicon-qc`
* **`--plot-melt` Option** (v0.6.1): Generate melt curve plots during qPCR workflow

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

#### Optional: ViennaRNA (for Secondary Structure)

For enhanced secondary structure prediction in amplicon analysis, install ViennaRNA:

```bash
# Ubuntu/Debian
sudo apt-get install vienna-rna

# macOS (Homebrew)  
brew install viennarna

# Conda (all platforms)
conda install -c bioconda viennarna
```

Without ViennaRNA, PrimerLab uses a fallback estimation method.

#### Option 2: For End Users (From GitHub Release)

```bash
# Install directly from GitHub (latest release)
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.4.3
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

**Primer Compatibility Check (v0.4.0):**

```bash
# Check if multiple primer pairs can work together
primerlab check-compat --primers primer_set.json

# With custom output directory
primerlab check-compat --primers primer_set.json --output results/

# Integrated with PCR design (auto-check after design)
primerlab run pcr --config design.yaml --check-compat
```

Example `primer_set.json`:

```json
[
  {"name": "GAPDH", "fwd": "ATGGGGAAGGTGAAGGTCGG", "rev": "GGATCTCGCTCCTGGAAGATG", "tm": 60.0},
  {"name": "ACTB", "fwd": "CATGTACGTTGCTATCCAGGC", "rev": "CTCCTTAATGTCACGCACGAT", "tm": 59.0}
]
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

| Section | Description |
|---------|-------------|
| [Getting Started](docs/getting-started.md) | Installation and first steps |
| [CLI Reference](docs/cli/README.md) | All 13 commands |
| [Configuration](docs/configuration/README.md) | YAML config reference |
| [Presets](docs/configuration/presets.md) | Pre-configured parameter sets |
| [API Reference](docs/api/README.md) | Programmatic interface |
| [Features](docs/features/README.md) | Advanced features |
| [Troubleshooting](docs/troubleshooting.md) | Common issues and solutions |

**Additional Resources:**

* [CHANGELOG](CHANGELOG.md) — Version history
* [STRUCTURE](STRUCTURE.md) — Project architecture
* [RELEASE_NOTES](RELEASE_NOTES.md) — Latest release highlights

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
├── tests/                # 506 automated tests
├── docs/                 # User documentation
├── examples/             # Example files
│   └── insilico/         # In-silico PCR examples
└── .dev/                 # Internal dev docs
```

---

## 📌 Development Status

### ✅ **v0.4.3** (Current)

* **Tm Gradient Simulation** (`primerlab tm-gradient`):
  * Optimal annealing temperature prediction
  * Temperature sensitivity analysis
  * Markdown/CSV/JSON reports
* **Batch Species-Check**:
  * Parallel processing with ThreadPoolExecutor
  * SQLite alignment caching
  * Directory-based primer loading
* **506 Tests** - Comprehensive test coverage

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

We welcome contributions! Please read our guidelines first:

📄 **[CONTRIBUTING.md](CONTRIBUTING.md)** — How to contribute, coding standards, PR checklist

Key principles:

* No cross-layer imports
* Deterministic, reproducible outputs
* All features need tests

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
