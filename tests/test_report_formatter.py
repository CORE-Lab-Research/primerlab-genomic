"""
Tests for Report and Formatter Modules - v0.8.1 Phase 2

Target: Increase coverage from 69% to 80%+
Focus: Low-coverage modules (formatter, report generator, json_export)
"""
import pytest
import tempfile
import os


# ============================================================================
# CLI FORMATTER TESTS (cli/formatter.py)
# ============================================================================

class TestOutputLevel:
    """Tests for OutputLevel enum."""
    
    def test_output_levels_exist(self):
        """Should have all output levels."""
        from primerlab.cli.formatter import OutputLevel
        
        assert OutputLevel.QUIET.value == 0
        assert OutputLevel.NORMAL.value == 1
        assert OutputLevel.VERBOSE.value == 2
        assert OutputLevel.DEBUG.value == 3


class TestColor:
    """Tests for Color class."""
    
    def test_color_codes_exist(self):
        """Should have basic color codes."""
        from primerlab.cli.formatter import Color
        
        # Color codes should be strings
        assert isinstance(Color.RESET, str)
        assert isinstance(Color.RED, str)
        assert isinstance(Color.GREEN, str)
        assert isinstance(Color.YELLOW, str)
    
    def test_color_disable(self):
        """Should be able to disable colors."""
        from primerlab.cli.formatter import Color
        
        # Store originals
        original_reset = Color.RESET
        original_red = Color.RED
        
        # Disable and verify
        Color.disable()
        assert Color.RESET == ""
        assert Color.RED == ""
        
        # Restore for other tests
        Color.RESET = original_reset
        Color.RED = original_red


class TestCLIFormatter:
    """Tests for CLIFormatter class."""
    
    def test_formatter_init_default(self):
        """Should initialize with default level."""
        from primerlab.cli.formatter import CLIFormatter, OutputLevel
        
        formatter = CLIFormatter()
        assert formatter.level == OutputLevel.NORMAL
    
    def test_formatter_init_custom(self):
        """Should initialize with custom level."""
        from primerlab.cli.formatter import CLIFormatter, OutputLevel
        
        formatter = CLIFormatter(level=OutputLevel.VERBOSE)
        assert formatter.level == OutputLevel.VERBOSE
    
    def test_should_print_normal(self):
        """Should check print level correctly."""
        from primerlab.cli.formatter import CLIFormatter, OutputLevel
        
        formatter = CLIFormatter(level=OutputLevel.NORMAL)
        assert formatter._should_print(OutputLevel.QUIET) == True
        assert formatter._should_print(OutputLevel.NORMAL) == True
        assert formatter._should_print(OutputLevel.VERBOSE) == False
    
    def test_header_prints(self):
        """Should print header without error."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.header("Test Header")  # Should not raise
    
    def test_subheader_prints(self):
        """Should print subheader without error."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.subheader("Test Subheader")
    
    def test_success_prints(self):
        """Should print success message."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.success("Test success")
    
    def test_error_prints(self):
        """Should print error message."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.error("Test error")
    
    def test_warning_prints(self):
        """Should print warning message."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.warning("Test warning")
    
    def test_info_prints(self):
        """Should print info message."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.info("Test info")
    
    def test_detail_verbose_only(self):
        """Should print detail only in verbose mode."""
        from primerlab.cli.formatter import CLIFormatter, OutputLevel
        
        # In normal mode
        formatter = CLIFormatter(level=OutputLevel.NORMAL)
        formatter.detail("This should not print")
        
        # In verbose mode
        formatter = CLIFormatter(level=OutputLevel.VERBOSE)
        formatter.detail("This should print")
    
    def test_debug_debug_only(self):
        """Should print debug only in debug mode."""
        from primerlab.cli.formatter import CLIFormatter, OutputLevel
        
        formatter = CLIFormatter(level=OutputLevel.DEBUG)
        formatter.debug("Debug message")
    
    def test_grade_prints(self):
        """Should print grade with color."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.grade("A", 95.0)
        formatter.grade("F", 30.0)
    
    def test_grade_color(self):
        """Should return correct color for grade."""
        from primerlab.cli.formatter import CLIFormatter, Color
        
        formatter = CLIFormatter()
        assert formatter._grade_color("A") == Color.GREEN
        assert formatter._grade_color("F") == Color.RED
        assert formatter._grade_color("X") == Color.WHITE
    
    def test_table_row_prints(self):
        """Should print table row."""
        from primerlab.cli.formatter import CLIFormatter, Color
        
        formatter = CLIFormatter()
        formatter.table_row("Label", "Value")
        formatter.table_row("Colored", "Value", Color.GREEN)
    
    def test_divider_prints(self):
        """Should print divider."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.divider()
    
    def test_blank_prints(self):
        """Should print blank line."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.blank()
    
    def test_spinner_start_end(self):
        """Should print spinner start/end."""
        from primerlab.cli.formatter import CLIFormatter
        
        formatter = CLIFormatter()
        formatter.spinner_start("Loading")
        formatter.spinner_end(success=True)
        
        formatter.spinner_start("Loading")
        formatter.spinner_end(success=False)


class TestGetFormatter:
    """Tests for get_formatter function."""
    
    def test_get_formatter_default(self):
        """Should return normal formatter by default."""
        from primerlab.cli.formatter import get_formatter, OutputLevel
        
        formatter = get_formatter()
        assert formatter.level == OutputLevel.NORMAL
    
    def test_get_formatter_verbose(self):
        """Should return verbose formatter."""
        from primerlab.cli.formatter import get_formatter, OutputLevel
        
        formatter = get_formatter(verbose=True)
        assert formatter.level == OutputLevel.VERBOSE
    
    def test_get_formatter_quiet(self):
        """Should return quiet formatter."""
        from primerlab.cli.formatter import get_formatter, OutputLevel
        
        formatter = get_formatter(quiet=True)
        assert formatter.level == OutputLevel.QUIET


class TestSupportsColor:
    """Tests for supports_color function."""
    
    def test_supports_color_returns_bool(self):
        """Should return boolean."""
        from primerlab.cli.formatter import supports_color
        
        result = supports_color()
        assert isinstance(result, bool)


# ============================================================================
# REPORT GENERATOR TESTS (core/report/generator.py)
# ============================================================================

class TestReportGenerator:
    """Tests for ReportGenerator class."""
    
    def test_generator_init(self):
        """Should initialize report generator."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        assert gen.report is not None
    
    def test_add_design(self):
        """Should add design summary."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT",
            forward_tm=60.0,
            reverse_tm=60.0,
            forward_gc=50.0,
            reverse_gc=50.0,
            product_size=200,
            quality_score=85.0
        )
        assert gen.report.design.has_primers
    
    def test_add_validation(self):
        """Should add validation summary."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_validation(
            amplicons=1,
            product_size=200,
            success_probability=0.95
        )
        assert gen.report.validation.validated
    
    def test_add_offtarget(self):
        """Should add off-target summary."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_offtarget(
            database="nt",
            forward_hits=2,
            reverse_hits=1,
            grade="A",
            score=95.0
        )
        assert gen.report.offtarget.checked
    
    def test_generate_report(self):
        """Should generate report."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        report = gen.generate()
        assert report is not None
    
    def test_to_markdown(self):
        """Should generate markdown output."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        markdown = gen.to_markdown()
        assert isinstance(markdown, str)
        assert len(markdown) > 0
    
    def test_to_json(self):
        """Should generate JSON output."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        json_str = gen.to_json()
        assert isinstance(json_str, str)
    
    def test_save_markdown(self):
        """Should save markdown report to file."""
        from primerlab.core.report.generator import ReportGenerator, ReportFormat
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.md")
            gen.save(path, format=ReportFormat.MARKDOWN)
            assert os.path.exists(path)


class TestGenerateReportFunction:
    """Tests for generate_report convenience function."""
    
    def test_generate_report_none_input(self):
        """Should handle None input gracefully."""
        from primerlab.core.report.generator import generate_report
        
        result = generate_report(None)
        assert result is not None


# ============================================================================
# JSON EXPORT TESTS (core/report/json_export.py)
# ============================================================================

class TestJSONExporter:
    """Tests for JSONExporter class."""
    
    def _create_test_report(self):
        """Create a test PrimerReport for testing."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT",
            forward_tm=60.0,
            reverse_tm=60.0,
            product_size=200
        )
        return gen.generate()
    
    def test_exporter_init(self):
        """Should initialize JSON exporter."""
        from primerlab.core.report.json_export import JSONExporter
        
        report = self._create_test_report()
        exporter = JSONExporter(report)
        assert exporter.report is not None
    
    def test_generate_json(self):
        """Should generate JSON string."""
        from primerlab.core.report.json_export import JSONExporter
        import json
        
        report = self._create_test_report()
        exporter = JSONExporter(report)
        json_str = exporter.generate()
        
        assert isinstance(json_str, str)
        # Should be valid JSON
        data = json.loads(json_str)
        assert "metadata" in data
    
    def test_generate_with_options(self):
        """Should generate JSON with options."""
        from primerlab.core.report.json_export import JSONExporter
        
        report = self._create_test_report()
        exporter = JSONExporter(report)
        
        # Test various options
        json_str = exporter.generate(include_metadata=False)
        assert "metadata" not in json_str or '"metadata"' not in json_str
        
        json_str = exporter.generate(pretty=False)
        assert isinstance(json_str, str)
    
    def test_save_json(self):
        """Should save JSON to file."""
        from primerlab.core.report.json_export import JSONExporter
        
        report = self._create_test_report()
        exporter = JSONExporter(report)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            exporter.save(path)
            assert os.path.exists(path)


class TestExportJsonFunction:
    """Tests for export_json convenience function."""
    
    def test_export_json(self):
        """Should export JSON using convenience function."""
        from primerlab.core.report.json_export import export_json
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        report = gen.generate()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            export_json(report, path)
            assert os.path.exists(path)


class TestReportExporter:
    """Tests for ReportExporter unified class."""
    
    def _create_test_report(self):
        """Create test report."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        return gen.generate()
    
    def test_exporter_init(self):
        """Should initialize unified exporter."""
        from primerlab.core.report.json_export import ReportExporter
        
        report = self._create_test_report()
        exporter = ReportExporter(report)
        assert exporter.report is not None
    
    def test_export_json_format(self):
        """Should export as JSON."""
        from primerlab.core.report.json_export import ReportExporter
        
        report = self._create_test_report()
        exporter = ReportExporter(report)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.json")
            result = exporter.export(path, format="json")
            assert os.path.exists(result)
    
    def test_export_markdown_format(self):
        """Should export as Markdown."""
        from primerlab.core.report.json_export import ReportExporter
        
        report = self._create_test_report()
        exporter = ReportExporter(report)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.md")
            result = exporter.export(path, format="markdown")
            assert os.path.exists(result)


# ============================================================================
# HTML EXPORT TESTS (core/report/html_export.py)
# ============================================================================

class TestHTMLExporter:
    """Tests for HTMLExporter class."""
    
    def _create_test_report(self):
        """Create a test report."""
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT",
            forward_tm=60.0,
            reverse_tm=60.0,
            product_size=200
        )
        gen.add_validation(amplicons=1, product_size=200, success_probability=0.95)
        gen.add_offtarget(database="nt", forward_hits=2, reverse_hits=1, grade="A", score=95.0)
        return gen.generate()
    
    def test_exporter_init(self):
        """Should initialize HTML exporter."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        assert exporter.report is not None
    
    def test_generate_html(self):
        """Should generate HTML string."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        html = exporter.generate()
        
        assert isinstance(html, str)
        assert "<html" in html
        assert "</html>" in html
    
    def test_grade_class(self):
        """Should return correct CSS class for grade."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        
        assert "A" in exporter._grade_class("A") or exporter._grade_class("A") != ""
    
    def test_badge_class(self):
        """Should return correct badge class."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        
        result = exporter._badge_class("A")
        assert isinstance(result, str)
    
    def test_header_section(self):
        """Should generate header section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        header = exporter._header_section()
        
        assert isinstance(header, str)
    
    def test_design_section(self):
        """Should generate design section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        design = exporter._design_section()
        
        assert isinstance(design, str)
    
    def test_validation_section(self):
        """Should generate validation section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        validation = exporter._validation_section()
        
        assert isinstance(validation, str)
    
    def test_offtarget_section(self):
        """Should generate off-target section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        offtarget = exporter._offtarget_section()
        
        assert isinstance(offtarget, str)
    
    def test_warnings_section(self):
        """Should generate warnings section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        warnings = exporter._warnings_section()
        
        assert isinstance(warnings, str)
    
    def test_footer_section(self):
        """Should generate footer section."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        footer = exporter._footer_section()
        
        assert isinstance(footer, str)
    
    def test_save_html(self):
        """Should save HTML to file."""
        from primerlab.core.report.html_export import HTMLExporter
        
        report = self._create_test_report()
        exporter = HTMLExporter(report)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.html")
            exporter.save(path)
            assert os.path.exists(path)
            
            # Check content
            with open(path, 'r') as f:
                content = f.read()
                assert "<html" in content


class TestExportHtmlFunction:
    """Tests for export_html convenience function."""
    
    def test_export_html(self):
        """Should export HTML using convenience function."""
        from primerlab.core.report.html_export import export_html
        from primerlab.core.report.generator import ReportGenerator
        
        gen = ReportGenerator()
        gen.add_design(
            forward_seq="ATCGATCGATCGATCGATCG",
            reverse_seq="CGATCGATCGATCGATCGAT"
        )
        report = gen.generate()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "report.html")
            export_html(report, path)
            assert os.path.exists(path)

