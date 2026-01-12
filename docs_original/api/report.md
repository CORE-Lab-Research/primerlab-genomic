# Report API

Report generation and export functionality.

## Module

```python
from primerlab.core.report import (
    ReportGenerator,
    ReportExporter,
    PrimerReport,
    HTMLExporter,
    MarkdownExporter,
    JSONExporter
)
```

---

## ReportGenerator

Generate structured reports from design results.

### Constructor

```python
generator = ReportGenerator(
    title: str = "Primer Design Report",
    include_scoring: bool = True,
    include_validation: bool = True
)
```

### Methods

#### set_design_data()

```python
generator.set_design_data(
    primers: List[PrimerPair],
    scores: Dict[str, float],
    workflow: str = "pcr"
)
```

#### set_validation_data()

```python
generator.set_validation_data(
    insilico_result: InsilicoPCRResult,
    blast_result: BlastResult = None
)
```

#### generate()

```python
report = generator.generate() -> PrimerReport
```

### Example: Full Report Generation

```python
from primerlab.core.report import ReportGenerator

# Create generator
generator = ReportGenerator(
    title="GFP Primer Design",
    include_scoring=True,
    include_validation=True
)

# Add design data
generator.set_design_data(
    primers=design_result.primers,
    scores={"overall": 95.5, "tm_balance": 98.0},
    workflow="pcr"
)

# Add validation data (optional)
generator.set_validation_data(
    insilico_result=validation_result,
    blast_result=offtarget_result
)

# Generate report object
report = generator.generate()
print(f"Report generated: {report.title}")
print(f"Primers: {len(report.design_summary.primers)}")
```

---

## ReportExporter

Export reports to various formats.

### Constructor

```python
exporter = ReportExporter(report: PrimerReport)
```

### Methods

#### export()

```python
exporter.export(
    output_path: str,
    format: str = "html"  # "html", "markdown", "json"
)
```

#### to_html() / to_markdown() / to_json()

```python
html_string = exporter.to_html()
md_string = exporter.to_markdown()
json_string = exporter.to_json()
```

### Example: Export to Multiple Formats

```python
from primerlab.core.report import ReportExporter

exporter = ReportExporter(report)

# Export to HTML (with dark/light mode toggle)
exporter.export("report.html", format="html")

# Export to Markdown (git-friendly)
exporter.export("report.md", format="markdown")

# Export to JSON (for pipelines)
exporter.export("report.json", format="json")
```

### Example: Get String Output

```python
# Get raw string (for further processing)
html_content = exporter.to_html()
md_content = exporter.to_markdown()

# Write with custom logic
with open("custom_report.html", "w") as f:
    f.write(html_content)
```

---

## HTMLExporter

Direct HTML export with theme support.

### Features

- Dark/light mode toggle
- Responsive design
- Interactive sections
- Collapsible details

### Example

```python
from primerlab.core.report import HTMLExporter

html_exporter = HTMLExporter(report)
html_exporter.export("beautiful_report.html")
```

---

## Complete Workflow Example

```python
from primerlab.api import design_pcr_primers
from primerlab.core.insilico import run_insilico_pcr
from primerlab.core.report import ReportGenerator, ReportExporter

# 1. Design primers
design = design_pcr_primers(
    sequence="ATGGTGAGCAAGGGCGAGGAG...",
    output_dir="output/"
)

# 2. Validate
validation = run_insilico_pcr(
    forward=design.primers[0].forward.sequence,
    reverse=design.primers[0].reverse.sequence,
    template_seq="ATGGTGAGCAAGGGCGAGGAG..."
)

# 3. Generate report
generator = ReportGenerator(title="My Primer Report")
generator.set_design_data(design.primers, design.scores)
generator.set_validation_data(validation)
report = generator.generate()

# 4. Export
exporter = ReportExporter(report)
exporter.export("final_report.html", format="html")
exporter.export("final_report.md", format="markdown")

print("Reports generated successfully!")
```

---

## See Also

- [Public API](public.md)
- [In-silico API](insilico.md)
- [Models Reference](models.md)
