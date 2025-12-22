# Example Report Output (v0.3.3)

This directory contains example report outputs from PrimerLab.

## Generating Reports

```bash
# Markdown report
primerlab run --config my.yaml --report --report-format markdown --report-output report.md

# HTML report (dark mode, interactive)
primerlab run --config my.yaml --report --report-format html --report-output report.html

# JSON report (machine-readable)
primerlab run --config my.yaml --report --report-format json --report-output report.json
```

## Sample Report Structure

### Markdown

```markdown
# 🧬 PrimerLab Report

**Generated:** 2024-01-15 10:30:00
**Version:** PrimerLab v0.3.3
**Overall Grade:** **A** (92.5/100)

## 🔬 Design Summary

| Primer | Sequence | Length | Tm | GC% |
|--------|----------|--------|-----|-----|
| Forward | `ATGCGATCGATCGATCGATC` | 20bp | 60.1°C | 50.0% |
| Reverse | `GCTAGCTAATCGATCGATCG` | 20bp | 59.8°C | 50.0% |

**Product Size:** 250bp

## ✅ Validation

- **Amplicons Predicted:** 1
- **Primary Product:** 250bp
- **PCR Success:** 95%

## 🎯 Off-target Analysis

- **Forward Hits:** 0
- **Reverse Hits:** 1
- **Specificity Grade:** **A** (95.0/100)
```

### HTML Features

- 🌙 Dark mode UI with gradient backgrounds
- 📊 Collapsible sections (click to expand/collapse)
- 📱 Responsive design for mobile
- 🎨 Color-coded grades (A=green, F=red)

### JSON Structure

```json
{
  "metadata": {
    "report_id": "",
    "created_at": "2024-01-15T10:30:00",
    "primerlab_version": "0.3.3"
  },
  "overall": {
    "grade": "A",
    "score": 92.5,
    "warnings": [],
    "recommendations": []
  },
  "design": {
    "forward_primer": {
      "name": "Forward",
      "sequence": "ATGCGATCGATCGATCGATC",
      "length": 20,
      "tm": 60.1,
      "gc_percent": 50.0
    },
    "reverse_primer": {...}
  },
  "validation": {...},
  "offtarget": {...}
}
```

## Programmatic Usage

```python
from primerlab.core.report import (
    ReportGenerator,
    HTMLExporter,
    JSONExporter
)

# Create report
generator = ReportGenerator()
generator.add_design(
    forward_seq="ATGCGATCGATCGATCGATC",
    reverse_seq="GCTAGCTAATCGATCGATCG",
    forward_tm=60.1,
    reverse_tm=59.8,
    forward_gc=50.0,
    reverse_gc=50.0,
    product_size=250
).add_offtarget(
    forward_hits=0,
    reverse_hits=1,
    grade="A",
    score=95.0
)

# Export in different formats
report = generator.generate()

# Markdown
print(generator.to_markdown())

# HTML
html_exporter = HTMLExporter(report)
html_exporter.save("report.html")

# JSON
json_exporter = JSONExporter(report)
json_exporter.save("report.json")
```
