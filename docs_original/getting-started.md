# Getting Started

## Installation Options

PrimerLab offers multiple installation methods. Choose the one that best fits your needs:

| Method | Best For | Includes External Tools |
|--------|----------|------------------------|
| **Docker** | Zero-setup, cross-platform | ✅ ViennaRNA, BLAST |
| **Conda** | Bioinformatics users | ✅ ViennaRNA, BLAST |
| **Pip** | Python developers | ❌ Manual install |

---

### Option 1: Docker (Recommended for beginners)

```bash
# Pull the image
docker pull ghcr.io/engkinandatama/primerlab-genomic:latest

# Run with your config file
docker run -v $(pwd):/data primerlab-genomic run pcr --config /data/config.yaml
```

No installation needed - everything is included!

---

### Option 2: Conda/Mamba

```bash
# Clone repository
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic

# Create environment (includes ViennaRNA, BLAST)
conda env create -f environment.yml
conda activate primerlab

# Install PrimerLab
pip install -e .
```

For faster install, use [Mamba](https://mamba.readthedocs.io/):

```bash
mamba env create -f environment.yml
```

---

### Option 3: Pip (Advanced)

Requires manual installation of system tools.

**Linux (Ubuntu/Debian):**

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y vienna-rna ncbi-blast+ build-essential

# Install PrimerLab
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.9.0
```

**macOS:**

```bash
brew install viennarna blast
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.9.0
```

**Windows:**

Use WSL (Windows Subsystem for Linux) and follow Linux instructions.

---

### Option 4: From Source (Development)

```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
pip install -e ".[dev]"
```

---

## Verify Installation

```bash
primerlab --version
# Output: PrimerLab v0.9.0

primerlab health
# Shows dependency status (ViennaRNA, BLAST, Primer3)
```

---

## Quick Start

### 1. Check Your Sequence

```bash
primerlab stats input.fasta
```

### 2. Create Config File

```bash
primerlab init --workflow pcr --output my_config.yaml
```

### 3. Run Primer Design

```bash
primerlab run pcr --config my_config.yaml
```

### 4. View Results

Results are saved in the output directory:

- `result.json` - Machine-readable results
- `report.md` - Human-readable report
- `audit.json` - Reproducibility log

---

## Troubleshooting

### primer3-py fails to install

```bash
# Install build tools first
sudo apt-get install -y build-essential python3-dev
```

### ViennaRNA not found

```bash
# Check if installed
RNAfold --version

# If not, install via apt or conda
sudo apt-get install vienna-rna
# or
conda install -c bioconda viennarna
```

### BLAST not found

```bash
# Check if installed
blastn -version

# If not, install
sudo apt-get install ncbi-blast+
```

---

## Next Steps

- [CLI Reference](cli/README.md) - All available commands
- [Configuration](configuration/README.md) - Config file options
- [Examples](../examples/README.md) - Example configurations
