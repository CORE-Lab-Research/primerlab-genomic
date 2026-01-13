# 🧬 PrimerLab Genomic

A modular bioinformatics framework for automated **primer and probe design**, built with clean architecture and reproducible workflows.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-GPLv2-blue.svg)](LICENSE)
[![Tests](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml/badge.svg)](https://github.com/engkinandatama/primerlab-genomic/actions/workflows/test.yml)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/engkinandatama/primerlab-genomic/pkgs/container/primerlab-genomic)
[![Docs](https://img.shields.io/badge/docs-Mintlify-0D9488.svg)](https://primerlab-genomic.mintlify.app/)
[![DeepWiki](https://img.shields.io/badge/docs-DeepWiki-blue.svg)](https://deepwiki.com/engkinandatama/primerlab-genomic)
[![PyPI](https://img.shields.io/pypi/v/primerlab-genomic.svg)](https://pypi.org/project/primerlab-genomic/)
[![Status](https://img.shields.io/badge/status-v1.0.1-brightgreen.svg)](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v1.0.1)

> 🔰 **Latest Release**: [**v1.0.0 - Stable Release**](https://github.com/engkinandatama/primerlab-genomic/releases/tag/v1.0.0) 🎉

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

### 📦 Feature Highlights

| Category | Features |
|----------|----------|
| **Primer Design** | PCR, qPCR, Nested PCR, Semi-Nested PCR |
| **Analysis** | BLAST off-target, In-silico PCR, Dimer matrix |
| **qPCR Tools** | TaqMan probe design, Melt curve, Efficiency calc |
| **Quality Control** | Hairpin, Homodimer, Heterodimer, Tm balance |
| **Species Check** | Cross-reactivity, Multi-species comparison |
| **Batch Processing** | Parallel processing, SQLite caching, CSV export |
| **Visualization** | Coverage maps, Melt curves, Dimer heatmaps |
| **Export** | JSON, Markdown, HTML, Excel, IDT plate format |

### 📚 Documentation

| Resource | Link |
|----------|------|
| **Getting Started** | [Installation & Quick Start](https://primerlab-genomic.mintlify.app/docs/getting-started) |
| **CLI Reference** | [Command Reference](https://primerlab-genomic.mintlify.app/docs/reference/cli) |
| **API Reference** | [Python API](https://primerlab-genomic.mintlify.app/docs/reference/api) |
| **Tutorials** | [Step-by-Step Guides](https://primerlab-genomic.mintlify.app/docs/tutorials) |
| **Changelog** | [Version History](CHANGELOG.md) |

---

## 🚀 Quick Start

### Installation

#### Option 1: PyPI (Recommended)

```bash
pip install primerlab-genomic
```

#### Option 2: Docker (No setup required)

```bash
# Pull and run
docker pull ghcr.io/engkinandatama/primerlab-genomic:1.0.0
docker run ghcr.io/engkinandatama/primerlab-genomic:1.0.0 --version

# Run with your config
docker run -v $(pwd):/data ghcr.io/engkinandatama/primerlab-genomic:1.0.0 run pcr --config /data/config.yaml
```

#### Option 3: From Source (For Development)

```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
pip install -e .
```

#### Optional: ViennaRNA (for Secondary Structure)

```bash
# Via pip (recommended)
pip install viennarna

# Via Conda
conda install -c bioconda viennarna
```

Without ViennaRNA, PrimerLab uses a fallback estimation method.

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

**qPCR Analysis Commands (v0.6.0):**

```bash
# Check TaqMan probe binding
primerlab probe-check --probe ATGCGATCGATCGATCGATCG

# Predict SYBR melt curve
primerlab melt-curve --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCG --format svg

# Validate qPCR amplicon quality
primerlab amplicon-qc --amplicon ATGCGATCGATCGATCGATCGATCGATCGATCG

# Generate melt plot during workflow (v0.6.1)
primerlab run qpcr --config design.yaml --plot-melt --plot-format png
```

**PCR Variants (v0.7.0):**

```bash
# Design Nested PCR primers
primerlab nested-design --sequence "ATGC..." --outer-size 400-600 --inner-size 150-250

# Design Semi-Nested PCR (shared forward primer)
primerlab seminested-design --sequence "ATGC..." --shared forward
```

**Analysis Tools (v0.7.1):**

```bash
# Analyze primer dimer matrix
primerlab dimer-matrix --primers primers.json --format svg

# Compare batch design runs
primerlab compare-batch result1.json result2.json --format markdown
```

**Visualization (v0.7.2):**

```bash
# Generate coverage map
primerlab coverage-map --result result.json --format svg
```

**qPCR Efficiency (v0.7.4):**

```bash
# Calculate efficiency from standard curve
primerlab qpcr-efficiency calculate --data curve.json

# Predict primer efficiency
primerlab qpcr-efficiency predict --forward "ATGCATGC..." --reverse "GCATGCAT..."
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
| [CLI Reference](docs/reference/cli/index.md) | All 25+ commands |
| [Configuration](docs/reference/config.md) | YAML config reference |
| [Presets](docs/reference/presets.md) | Pre-configured parameter sets |
| [API Reference](docs/reference/api/index.md) | Programmatic interface |
| [Features](docs/concepts/features/index.md) | Advanced features |
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
├── tests/                # 1286 automated tests
├── docs/                 # User documentation
├── examples/             # Example files
│   └── insilico/         # In-silico PCR examples
└── .dev/                 # Internal dev docs
```

---

## 📌 Development Status

### ✅ **v1.0.0** (Current)

* **Performance Optimization** (`core/cache.py`):
  * LRU caching for Tm, GC, and ΔG calculations
  * 2-5x speedup for repeated computations
* **Model Standardization** (v0.8.2):
  * `to_dict()` methods for 10+ dataclasses
  * Comprehensive STRUCTURE.md documentation
* **Code Quality Foundation** (v0.8.0):
  * Type hints infrastructure (mypy config)
  * Exception testing (20+ tests)
  * Flake8 fixes (8,600+ fixes)
* **1286 Tests** - Comprehensive test coverage

### v0.7.x Features (PCR Variants & qPCR Advanced)

* **Nested PCR Design** (`core/variants/nested.py`)
* **Semi-Nested PCR** (`core/variants/seminested.py`)
* **Dimer Matrix Analysis** (`core/analysis/dimer_matrix.py`)
* **Batch Comparison** (`core/analysis/batch_compare.py`)
* **Coverage Map** (`core/visualization/coverage_map.py`)
* **qPCR Efficiency** (`core/qpcr/efficiency.py`)
* **Advanced qPCR** (`core/qpcr/advanced.py`): HRM, dPCR, quencher recommendations

### v0.6.x Features (Genotyping & Visualization)

* **Allele Discrimination** (`core/genotyping/`)
* **RT-qPCR Validation** (`core/rtpcr/`)
* **Melt Curve Visualization**
* **CLI Commands**: `probe-check`, `melt-curve`, `amplicon-qc`

### v0.5.0 Features

* Probe Binding Simulation (TaqMan Tm calculation)
* qPCR Amplicon Validation (Length/GC/structure)
* SYBR Melt Curve Prediction

### v0.4.x Features

* Primer Compatibility Check (v0.4.0)
* Amplicon Analysis (v0.4.1)
* Species Specificity (v0.4.2)
* Tm Gradient Simulation (v0.4.3)

### Earlier Versions

* v0.6.x: Allele discrimination, RT-qPCR, melt curve visualization
* v0.3.x: BLAST off-target, reporting, Tm correction
* v0.2.x: In-silico PCR simulation
* v0.1.x: Core design, stats, batch processing

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

This project is licensed under the **GNU General Public License v2.0 (GPL-2.0)**.
See the [LICENSE](LICENSE) file for details.

> **Note on Dependencies:**
> This project depends on [primer3-py](https://github.com/libnano/primer3-py) which is licensed under GPL-2.0.
> As such, PrimerLab Genomic adopts the compatible GPL-2.0 license to ensure compliance and freedom for end users.

© 2025–present — **Engki Nandatama**

---

## 🙏 Acknowledgments

* **Primer3** — Primary primer design engine
* **ViennaRNA** — Thermodynamic folding & secondary structure analysis

---

## 📬 Contact

For issues, suggestions, or contributions:

➡️ **[Open an issue on GitHub](https://github.com/engkinandatama/primerlab-genomic/issues)**
