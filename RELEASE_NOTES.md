# 🎉 PrimerLab v1.0.0 - Stable Release

**First production-ready release of PrimerLab!**

## Highlights

- ✅ **1286+ passing tests** with comprehensive coverage
- ✅ **Full PCR Workflows**: Standard PCR, qPCR, Nested PCR, Semi-Nested PCR
- ✅ **Complete Analysis Suite**: BLAST off-target, In-silico PCR, Dimer matrix
- ✅ **Multiple Installation Options**: Docker, Conda, Pip
- ✅ **Comprehensive Documentation**: API reference, CLI guide, tutorials

## Installation

### PyPI (Recommended)

```bash
pip install primerlab-genomic
```

### Docker

```bash
docker pull ghcr.io/engkinandatama/primerlab-genomic:1.0.0
docker run ghcr.io/engkinandatama/primerlab-genomic:1.0.0 --version
```

### Conda

```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
conda env create -f environment.yml
conda activate primerlab
pip install -e .
```

## Quick Start

```bash
# PCR primer design
primerlab run pcr --config your_config.yaml

# qPCR with TaqMan probe
primerlab run qpcr --config qpcr_config.yaml

# Nested PCR
primerlab run nested --config nested_config.yaml
```

## What's New in v1.0.0

### Added

- **Production Status**: Changed from Beta to Production/Stable
- **Report Standardization**: Unified report format across all workflows
- **Documentation**: Complete tutorials, API reference, configuration guide
- **Docker Support**: Multi-stage build with ViennaRNA and BLAST+ included
- **PyPI Publishing**: Automated release via GitHub Actions

### Changed  

- Version bump from 0.9.x to 1.0.0
- Updated all badges and documentation to reflect stable release

## Documentation

- 📚 [Full Documentation](https://engkinandatama.github.io/primerlab-genomic/)
- 🚀 [Getting Started](https://engkinandatama.github.io/primerlab-genomic/getting-started/)
- 📖 [CLI Reference](https://engkinandatama.github.io/primerlab-genomic/cli/README/)
- 🔧 [API Reference](https://engkinandatama.github.io/primerlab-genomic/api/README/)
- 📝 [Tutorials](https://engkinandatama.github.io/primerlab-genomic/tutorials/README/)

## Requirements

- Python 3.10+
- primer3-py >= 2.0.0
- biopython >= 1.80
- Optional: ViennaRNA, BLAST+ (included in Docker)

## Full Changelog

See [CHANGELOG.md](https://github.com/engkinandatama/primerlab-genomic/blob/main/CHANGELOG.md)
