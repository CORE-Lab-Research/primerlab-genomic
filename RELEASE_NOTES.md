# v0.2.0 - In-silico PCR Simulation

**Release Date:** 2025-12-18

## ✨ Highlights

This release introduces **In-silico PCR Simulation** - validate your primers against a template sequence before ordering!

- 🧬 Virtual PCR engine with binding site analysis
- 🎯 Multi-product prediction with likelihood scoring
- 📊 Primer alignment visualization in terminal
- 📁 FASTA export of predicted amplicons

---

## 🆕 New Features

### `primerlab insilico` Command

Simulate PCR amplification to validate primers:

```bash
primerlab insilico -p primers.json -t template.fasta
```

**Features:**

- Primer binding detection with mismatch tolerance
- 3' end stability analysis (minimum 3bp perfect match)
- 5' mismatch tolerance (up to 2bp)
- Product size validation
- Orientation check (primers facing each other)
- Multiple product prediction

**Output Files:**

- `insilico_result.json` - Complete results with binding data
- `predicted_amplicons.fasta` - Predicted amplicon sequences

---

## 🔧 Improvements

### Enhanced YAML Error Handling

- Shows line number and column of syntax errors
- Displays problematic line content
- Lists common YAML error tips

### Database Resilience

- SQLite integrity check on startup
- Auto-backup before repair operations
- Auto-recovery from corruption

---

## 📦 Installation

```bash
pip install primerlab-genomic==0.2.0
```

Or upgrade:

```bash
pip install --upgrade primerlab-genomic
```

---

## 📊 Test Coverage

- **228 tests passing**
- New: `test_insilico.py` (24 unit tests)
- New: `test_cli_insilico.py` (CLI integration)

---

## 📚 Documentation

- [CLI Reference: insilico](docs/cli/insilico.md)
- [Examples](examples/insilico/)

---

## 🗺️ Roadmap

Next releases before v1.0.0 stable:

| Version | Feature |
|---------|---------|
| v0.3.0 | BLAST Integration |
| v0.3.1 | SNP/Variant Check |
| v0.4.0 | Multiplex Analysis |
| v0.5.0 | qPCR Customization |
| v0.6.0 | Polish & Performance |
| **v1.0.0** | 🎉 Stable Release |

---

**Full Changelog:** [v0.1.6...v0.2.0](https://github.com/engkinandatama/primerlab-genomic/compare/v0.1.6...v0.2.0)
