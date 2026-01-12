---
title: "Report Generation"
description: "Feature documentation: Report Generation"
---
**v0.3.3** - Enhanced report generation with multiple formats.

## Overview

PrimerLab generates comprehensive reports after primer design workflows. Reports include:

- Design summary and scoring
- Validation results
- Off-target analysis
- Recommendations

## Formats

| Format | Description |
|--------|-------------|
| `markdown` | Human-readable, Git-friendly |
| `html` | Interactive with dark/light mode |
| `json` | Machine-readable for pipelines |

## CLI Usage

```bash
# Generate report after design
primerlab run pcr --config my_config.yaml --report

# Specify format
primerlab run pcr --config my_config.yaml \
  --report --report-format html --report-output report.html
```

## Report Contents

### Design Summary

- Primer sequences and properties
- Tm, GC%, length
- Overall design score (0-100)

### Validation

- In-silico PCR results
- Binding site analysis
- 3' stability assessment

### Off-target

- BLAST hit count
- Specificity grade (A-F)
- Risk assessment

## Programmatic Usage

```python
from primerlab.core.report import ReportGenerator, ReportExporter

# Create report
generator = ReportGenerator()
generator.set_design_data(primers, scores)
generator.set_validation_data(insilico_results)

# Export
exporter = ReportExporter(generator.report)
exporter.export("report.html", format="html")
```

## See Also

- [Run Command](../cli/run) - Report generation flags
- [Examples](../../examples/report/README) - Sample outputs
