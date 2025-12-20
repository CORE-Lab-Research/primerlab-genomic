# Getting Started

## Installation

### Option 1: From GitHub (Recommended)

```bash
pip install git+https://github.com/engkinandatama/primerlab-genomic.git@v0.2.5
```

### Option 2: From Source (Development)

```bash
git clone https://github.com/engkinandatama/primerlab-genomic.git
cd primerlab-genomic
pip install -e .
```

### WSL Users (Windows)

PrimerLab requires `primer3-py` which compiles native extensions. For best results on Windows:

1. **Use WSL2** (Windows Subsystem for Linux)
2. Install dependencies in WSL:

   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv
   ```

3. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

See [WSL Quickstart Guide](../.dev/Guide/wsl_quickstart.md) for detailed setup.

## Verify Installation

```bash
primerlab --version
# Output: PrimerLab v0.2.5

primerlab health
# Shows dependency status
```

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

## Next Steps

- [CLI Reference](cli/README.md) - All available commands
- [Configuration](configuration/README.md) - Config file options
- [Examples](../examples/README.md) - Example configurations
