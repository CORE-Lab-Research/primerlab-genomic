"""
HTML Export (v0.3.3)

Generate interactive HTML reports with collapsible sections.
"""

from typing import Optional
from pathlib import Path
from datetime import datetime

from primerlab.core.report.models import PrimerReport


class HTMLExporter:
    """
    Generate interactive HTML reports.
    
    Features:
    - Collapsible sections
    - Syntax highlighting for sequences
    - Responsive design
    - Dark mode support
    """
    
    # CSS styles for the report
    STYLES = """
    <style>
        :root {
            --bg-primary: #1a1a2e;
            --bg-secondary: #16213e;
            --bg-card: #0f3460;
            --text-primary: #e4e4e4;
            --text-secondary: #a9a9a9;
            --accent: #e94560;
            --success: #4ecca3;
            --warning: #ffc107;
            --danger: #dc3545;
            --info: #17a2b8;
        }
        
        /* Light mode */
        [data-theme="light"] {
            --bg-primary: #f5f5f5;
            --bg-secondary: #e0e0e0;
            --bg-card: #ffffff;
            --text-primary: #1a1a2e;
            --text-secondary: #555555;
        }
        
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
            transition: all 0.3s ease;
        }
        
        .container { max-width: 1000px; margin: 0 auto; }
        
        .theme-toggle {
            position: fixed;
            top: 1rem;
            right: 1rem;
            padding: 0.5rem 1rem;
            background: var(--bg-card);
            border: 1px solid var(--bg-secondary);
            color: var(--text-primary);
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            z-index: 1000;
        }
        
        .theme-toggle:hover { background: var(--bg-secondary); }
        
        header {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: var(--bg-secondary);
            border-radius: 12px;
        }
        
        h1 { color: var(--accent); font-size: 2rem; margin-bottom: 0.5rem; }
        h2 { color: var(--text-primary); font-size: 1.5rem; margin: 1rem 0; }
        h3 { color: var(--text-secondary); font-size: 1.2rem; }
        
        .meta { color: var(--text-secondary); font-size: 0.9rem; }
        
        .grade {
            display: inline-block;
            font-size: 3rem;
            font-weight: bold;
            padding: 1rem 2rem;
            border-radius: 12px;
            margin: 1rem 0;
        }
        
        .grade-A { background: var(--success); color: #000; }
        .grade-B { background: var(--info); color: #fff; }
        .grade-C { background: var(--warning); color: #000; }
        .grade-D { background: var(--danger); color: #fff; }
        .grade-F { background: var(--danger); color: #fff; }
        
        .card {
            background: var(--bg-card);
            border-radius: 12px;
            margin: 1rem 0;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .card-header {
            background: var(--bg-secondary);
            padding: 1rem;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-header:hover { opacity: 0.9; }
        
        .card-header::after {
            content: '▼';
            transition: transform 0.3s;
        }
        
        .card.collapsed .card-header::after {
            transform: rotate(-90deg);
        }
        
        .card.collapsed .card-body { display: none; }
        
        .card-body { padding: 1rem; }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--bg-secondary);
        }
        
        th { background: var(--bg-secondary); }
        
        .sequence {
            font-family: 'Consolas', 'Monaco', monospace;
            background: var(--bg-secondary);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: bold;
        }
        
        .badge-success { background: var(--success); color: #000; }
        .badge-warning { background: var(--warning); color: #000; }
        .badge-danger { background: var(--danger); color: #fff; }
        
        footer {
            text-align: center;
            margin-top: 2rem;
            padding: 1rem;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            body { padding: 1rem; }
            h1 { font-size: 1.5rem; }
            .grade { font-size: 2rem; }
            .theme-toggle { top: 0.5rem; right: 0.5rem; }
        }
    </style>
    """
    
    # JavaScript for interactivity
    SCRIPTS = """
    <script>
        // Collapsible cards
        document.querySelectorAll('.card-header').forEach(header => {
            header.addEventListener('click', () => {
                header.parentElement.classList.toggle('collapsed');
            });
        });
        
        // Theme toggle
        const themeToggle = document.querySelector('.theme-toggle');
        const html = document.documentElement;
        
        // Check saved preference
        const savedTheme = localStorage.getItem('primerlab-theme') || 'dark';
        html.setAttribute('data-theme', savedTheme);
        updateToggleText();
        
        themeToggle.addEventListener('click', () => {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('primerlab-theme', next);
            updateToggleText();
        });
        
        function updateToggleText() {
            const current = html.getAttribute('data-theme');
            themeToggle.textContent = current === 'dark' ? '☀️ Light' : '🌙 Dark';
        }
    </script>
    """
    
    def __init__(self, report: PrimerReport):
        """
        Initialize HTML exporter.
        
        Args:
            report: PrimerReport to export
        """
        self.report = report
    
    def _grade_class(self, grade: str) -> str:
        """Get CSS class for grade."""
        return f"grade-{grade}" if grade in "ABCDF" else ""
    
    def _badge_class(self, grade: str) -> str:
        """Get badge class for grade."""
        if grade in ["A", "B"]:
            return "badge-success"
        elif grade == "C":
            return "badge-warning"
        return "badge-danger"
    
    def generate(self) -> str:
        """
        Generate complete HTML report.
        
        Returns:
            HTML string
        """
        report = self.report
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PrimerLab Report - {report.created_at.strftime('%Y-%m-%d')}</title>
    {self.STYLES}
</head>
<body>
    <button class="theme-toggle">🌙 Dark</button>
    <div class="container">
        {self._header_section()}
        {self._design_section()}
        {self._validation_section()}
        {self._offtarget_section()}
        {self._warnings_section()}
        {self._footer_section()}
    </div>
    {self.SCRIPTS}
</body>
</html>"""
        
        return html
    
    def _header_section(self) -> str:
        """Generate header section."""
        r = self.report
        grade_class = self._grade_class(r.overall_grade)
        
        return f"""
        <header>
            <h1>🧬 PrimerLab Report</h1>
            <p class="meta">Generated: {r.created_at.strftime('%Y-%m-%d %H:%M:%S')} | Version: {r.primerlab_version}</p>
            <div class="grade {grade_class}">{r.overall_grade}</div>
            <p>Overall Score: {r.overall_score:.1f}/100</p>
        </header>
        """
    
    def _design_section(self) -> str:
        """Generate design section."""
        d = self.report.design
        
        if not d.has_primers:
            return ""
        
        fwd = d.forward_primer
        rev = d.reverse_primer
        
        return f"""
        <div class="card">
            <div class="card-header">
                <h2>🔬 Design Summary</h2>
            </div>
            <div class="card-body">
                <table>
                    <tr>
                        <th>Primer</th>
                        <th>Sequence</th>
                        <th>Length</th>
                        <th>Tm</th>
                        <th>GC%</th>
                    </tr>
                    <tr>
                        <td>Forward</td>
                        <td><span class="sequence">{fwd.sequence}</span></td>
                        <td>{fwd.length}bp</td>
                        <td>{fwd.tm:.1f}°C</td>
                        <td>{fwd.gc_percent:.1f}%</td>
                    </tr>
                    <tr>
                        <td>Reverse</td>
                        <td><span class="sequence">{rev.sequence}</span></td>
                        <td>{rev.length}bp</td>
                        <td>{rev.tm:.1f}°C</td>
                        <td>{rev.gc_percent:.1f}%</td>
                    </tr>
                </table>
                {f'<p><strong>Product Size:</strong> {d.product_size}bp</p>' if d.product_size else ''}
            </div>
        </div>
        """
    
    def _validation_section(self) -> str:
        """Generate validation section."""
        v = self.report.validation
        
        if not v.validated:
            return ""
        
        return f"""
        <div class="card">
            <div class="card-header">
                <h2>✅ Validation Results</h2>
            </div>
            <div class="card-body">
                <table>
                    <tr><td>Amplicons Predicted</td><td>{v.amplicons_predicted}</td></tr>
                    <tr><td>Primary Product</td><td>{v.primary_product_size or 'N/A'}bp</td></tr>
                    <tr><td>PCR Success Probability</td><td>{v.pcr_success_probability*100:.0f}%</td></tr>
                </table>
            </div>
        </div>
        """
    
    def _offtarget_section(self) -> str:
        """Generate off-target section."""
        o = self.report.offtarget
        
        if not o.checked:
            return ""
        
        badge_class = self._badge_class(o.combined_grade)
        
        return f"""
        <div class="card">
            <div class="card-header">
                <h2>🎯 Off-target Analysis</h2>
            </div>
            <div class="card-body">
                <table>
                    <tr><td>Database</td><td>{o.database or 'N/A'}</td></tr>
                    <tr><td>Forward Hits</td><td>{o.forward_hits}</td></tr>
                    <tr><td>Reverse Hits</td><td>{o.reverse_hits}</td></tr>
                    <tr>
                        <td>Specificity Grade</td>
                        <td><span class="badge {badge_class}">{o.combined_grade}</span> ({o.specificity_score:.1f}/100)</td>
                    </tr>
                </table>
            </div>
        </div>
        """
    
    def _warnings_section(self) -> str:
        """Generate warnings section."""
        warnings = self.report.warnings
        
        if not warnings:
            return ""
        
        items = "\n".join(f"<li>{w}</li>" for w in warnings)
        
        return f"""
        <div class="card">
            <div class="card-header">
                <h2>⚠️ Warnings</h2>
            </div>
            <div class="card-body">
                <ul>{items}</ul>
            </div>
        </div>
        """
    
    def _footer_section(self) -> str:
        """Generate footer section."""
        return f"""
        <footer>
            Generated by PrimerLab v{self.report.primerlab_version} | 
            <a href="https://github.com/primerlab" style="color: var(--accent);">Documentation</a>
        </footer>
        """
    
    def save(self, path: str):
        """
        Save HTML report to file.
        
        Args:
            path: Output file path
        """
        html = self.generate()
        Path(path).write_text(html, encoding="utf-8")


def export_html(report: PrimerReport, path: str):
    """
    Convenience function to export HTML report.
    
    Args:
        report: PrimerReport to export
        path: Output file path
    """
    exporter = HTMLExporter(report)
    exporter.save(path)
