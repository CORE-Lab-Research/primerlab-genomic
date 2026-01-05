"""
Direct Tests for Low-Coverage Modules - v0.8.1

Tests for modules with 0% coverage to increase overall coverage.
"""
import pytest
import tempfile
import os
import csv
import io


# ============================================================================
# BATCH GENERATOR TESTS
# ============================================================================

class TestBatchGenerator:
    """Direct tests for primerlab/cli/batch_generator.py."""
    
    def test_generate_configs_basic(self):
        """Should generate config files from CSV."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test CSV
            csv_path = os.path.join(tmpdir, "test.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence'])
                writer.writeheader()
                writer.writerow({'name': 'gene1', 'sequence': 'ATCGATCGATCGATCGATCG'})
                writer.writerow({'name': 'gene2', 'sequence': 'GCTAGCTAGCTAGCTAGCTA'})
            
            # Generate configs
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                workflow="pcr",
                show_progress=False
            )
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert os.path.exists(result[0])
    
    def test_generate_configs_with_tm_params(self):
        """Should generate configs with Tm parameters from CSV."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_tm.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence', 'tm_min', 'tm_max'])
                writer.writeheader()
                writer.writerow({
                    'name': 'gene1', 
                    'sequence': 'ATCGATCGATCGATCGATCG',
                    'tm_min': '58',
                    'tm_max': '62'
                })
            
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                show_progress=False
            )
            
            assert len(result) == 1
    
    def test_generate_configs_with_product_size(self):
        """Should generate configs with product size from CSV."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_product.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence', 'product_min', 'product_max'])
                writer.writeheader()
                writer.writerow({
                    'name': 'gene1', 
                    'sequence': 'ATCGATCGATCGATCGATCG',
                    'product_min': '100',
                    'product_max': '300'
                })
            
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                show_progress=False
            )
            
            assert len(result) == 1
    
    def test_generate_configs_with_gc_params(self):
        """Should generate configs with GC parameters from CSV."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_gc.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence', 'gc_min', 'gc_max'])
                writer.writeheader()
                writer.writerow({
                    'name': 'gene1', 
                    'sequence': 'ATCGATCGATCGATCGATCG',
                    'gc_min': '40',
                    'gc_max': '60'
                })
            
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                show_progress=False
            )
            
            assert len(result) == 1
    
    def test_generate_configs_skips_empty_rows(self):
        """Should skip rows with missing name or sequence."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test_empty.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence'])
                writer.writeheader()
                writer.writerow({'name': 'gene1', 'sequence': 'ATCGATCGATCGATCGATCG'})
                writer.writerow({'name': '', 'sequence': 'ATCGATCG'})  # Empty name
                writer.writerow({'name': 'gene3', 'sequence': ''})  # Empty sequence
            
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                show_progress=False
            )
            
            # Only first row should generate a config
            assert len(result) == 1
    
    def test_generate_configs_file_not_found(self):
        """Should raise error for non-existent CSV."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(FileNotFoundError):
                generate_configs_from_csv(
                    csv_path="/nonexistent/path.csv",
                    output_dir=tmpdir,
                    show_progress=False
                )
    
    def test_generate_configs_with_template(self):
        """Should use custom template if provided."""
        from primerlab.cli.batch_generator import generate_configs_from_csv
        
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            with open(csv_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['name', 'sequence'])
                writer.writeheader()
                writer.writerow({'name': 'gene1', 'sequence': 'ATCGATCGATCGATCGATCG'})
            
            custom_template = {
                "workflow": "qpcr",
                "parameters": {"tm": {"min": 55, "opt": 60, "max": 65}}
            }
            
            output_dir = os.path.join(tmpdir, "configs")
            result = generate_configs_from_csv(
                csv_path=csv_path,
                output_dir=output_dir,
                workflow="qpcr",
                template=custom_template,
                show_progress=False
            )
            
            assert len(result) == 1


# ============================================================================
# PROGRESS INDICATOR TESTS
# ============================================================================

class TestSpinner:
    """Direct tests for Spinner class."""
    
    def test_spinner_init(self):
        """Should initialize spinner with defaults."""
        from primerlab.cli.progress import Spinner
        
        spinner = Spinner()
        assert spinner.message == "Loading"
        assert spinner.delay == 0.1
    
    def test_spinner_init_custom(self):
        """Should initialize spinner with custom values."""
        from primerlab.cli.progress import Spinner
        
        spinner = Spinner(message="Processing", delay=0.2)
        assert spinner.message == "Processing"
        assert spinner.delay == 0.2
    
    def test_spinner_start_stop(self):
        """Should start and stop spinner."""
        from primerlab.cli.progress import Spinner
        import time
        
        spinner = Spinner(message="Test", delay=0.05)
        spinner.start()
        time.sleep(0.1)  # Let it spin briefly
        spinner.stop(success=True)
        
        assert spinner._thread is None
    
    def test_spinner_stop_failure(self):
        """Should display failure icon on stop(success=False)."""
        from primerlab.cli.progress import Spinner
        import time
        
        spinner = Spinner(message="Failing", delay=0.05)
        spinner.start()
        time.sleep(0.1)
        spinner.stop(success=False)
        
        assert spinner._thread is None
    
    def test_spinner_context_manager(self):
        """Should work as context manager."""
        from primerlab.cli.progress import Spinner
        
        with Spinner(message="Context Test", delay=0.05) as s:
            import time
            time.sleep(0.05)
        
        # Spinner should be stopped after context exit
        assert s._thread is None
    
    def test_spinner_frames(self):
        """Should have animation frames."""
        from primerlab.cli.progress import Spinner
        
        assert len(Spinner.FRAMES) > 0


class TestProgressBar:
    """Direct tests for ProgressBar class."""
    
    def test_progressbar_init(self):
        """Should initialize progress bar with defaults."""
        from primerlab.cli.progress import ProgressBar
        
        bar = ProgressBar(total=100)
        assert bar.total == 100
        assert bar.message == "Progress"
        assert bar.current == 0
    
    def test_progressbar_init_custom(self):
        """Should initialize progress bar with custom values."""
        from primerlab.cli.progress import ProgressBar
        
        bar = ProgressBar(total=50, message="Testing", width=40, show_eta=False)
        assert bar.total == 50
        assert bar.message == "Testing"
        assert bar.width == 40
        assert bar.show_eta == False
    
    def test_progressbar_update(self):
        """Should update progress."""
        from primerlab.cli.progress import ProgressBar
        
        bar = ProgressBar(total=10)
        bar.update()
        assert bar.current == 1
        bar.update(3)
        assert bar.current == 4
    
    def test_progressbar_set(self):
        """Should set progress to specific value."""
        from primerlab.cli.progress import ProgressBar
        
        bar = ProgressBar(total=100)
        bar.set(50)
        assert bar.current == 50
    
    def test_progressbar_render_zero_total(self):
        """Should handle zero total gracefully."""
        from primerlab.cli.progress import ProgressBar
        
        bar = ProgressBar(total=0)
        bar._render()  # Should not crash
    
    def test_progressbar_context_manager(self):
        """Should work as context manager."""
        from primerlab.cli.progress import ProgressBar
        
        with ProgressBar(total=5, message="CM Test") as bar:
            for i in range(5):
                bar.update()
        
        assert bar.current == 5


class TestProgressHelpers:
    """Tests for progress helper functions."""
    
    def test_spinner_context_function(self):
        """Should provide spinner context manager function."""
        from primerlab.cli.progress import spinner
        
        with spinner("Helper test"):
            import time
            time.sleep(0.05)
    
    def test_progress_context_function(self):
        """Should provide progress context manager function."""
        from primerlab.cli.progress import progress
        
        with progress(5, "Helper progress") as bar:
            for i in range(5):
                bar.update()
    
    def test_show_spinner_function(self):
        """Should run function with spinner."""
        from primerlab.cli.progress import show_spinner
        
        def dummy_func(x):
            import time
            time.sleep(0.05)
            return x * 2
        
        result = show_spinner("Computing", dummy_func, 5)
        assert result == 10


# ============================================================================
# CONSOLE OUTPUT TESTS  
# ============================================================================

class TestConsole:
    """Tests for primerlab/cli/console.py."""
    
    def test_print_header(self):
        """Should print styled header."""
        from primerlab.cli.console import print_header
        print_header("Test Header")
    
    def test_print_success(self):
        """Should print success message."""
        from primerlab.cli.console import print_success
        print_success("Operation successful")
    
    def test_print_warning(self):
        """Should print warning message."""
        from primerlab.cli.console import print_warning
        print_warning("This is a warning")
    
    def test_print_error(self):
        """Should print error message."""
        from primerlab.cli.console import print_error
        print_error("This is an error")
    
    def test_print_info(self):
        """Should print info message."""
        from primerlab.cli.console import print_info
        print_info("This is info")
    
    def test_create_progress_bar(self):
        """Should create Rich progress bar."""
        from primerlab.cli.console import create_progress_bar
        bar = create_progress_bar()
        assert bar is not None
    
    def test_console_theme(self):
        """Should have custom theme defined."""
        from primerlab.cli.console import PRIMERLAB_THEME, console
        assert PRIMERLAB_THEME is not None
        assert console is not None


# ============================================================================
# ALIGNMENT VIEW TESTS
# ============================================================================

class TestAlignmentView:
    """Tests for primerlab/core/report/alignment_view.py."""
    
    def test_alignment_match_create(self):
        """Should create AlignmentMatch dataclass."""
        from primerlab.core.report.alignment_view import AlignmentMatch
        
        match = AlignmentMatch(
            query_seq="ATCGATCGATCGATCGATCG",
            target_seq="ATCGATCGATCGATCGATCG",
            query_start=0,
            query_end=20,
            target_start=100,
            target_end=120,
            identity=100.0
        )
        assert match.identity == 100.0
        assert match.query_seq == "ATCGATCGATCGATCGATCG"
    
    def test_alignment_view_init(self):
        """Should initialize AlignmentView."""
        from primerlab.core.report.alignment_view import AlignmentView
        
        view = AlignmentView()
        assert view.use_colors == True
        assert view.line_width == 60
    
    def test_alignment_view_init_custom(self):
        """Should initialize with custom settings."""
        from primerlab.core.report.alignment_view import AlignmentView
        
        view = AlignmentView(use_colors=False, line_width=80)
        assert view.use_colors == False
        assert view.line_width == 80
    
    def test_format_alignment(self):
        """Should format alignment as ASCII."""
        from primerlab.core.report.alignment_view import AlignmentView, AlignmentMatch
        
        view = AlignmentView(use_colors=False)
        match = AlignmentMatch(
            query_seq="ATCGATCGATCGATCGATCG",
            target_seq="ATCGATCGATCGATCGATCG",
            query_start=0,
            query_end=20,
            target_start=100,
            target_end=120,
            identity=100.0
        )
        result = view.format_alignment(match)
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_format_binding_diagram(self):
        """Should format binding site diagram."""
        from primerlab.core.report.alignment_view import AlignmentView
        
        view = AlignmentView(use_colors=False)
        result = view.format_binding_diagram(
            target_length=1000,
            forward_pos=(100, 120),
            reverse_pos=(300, 320)
        )
        assert isinstance(result, str)
    
    def test_offtarget_table_init(self):
        """Should initialize OfftargetTable."""
        from primerlab.core.report.alignment_view import OfftargetTable
        
        table = OfftargetTable(use_colors=False)
        assert table.use_colors == False
    
    def test_offtarget_table_format_summary(self):
        """Should format off-target summary."""
        from primerlab.core.report.alignment_view import OfftargetTable
        
        table = OfftargetTable(use_colors=False)
        result = table.format_summary(
            forward_hits=2,
            reverse_hits=1,
            forward_grade="A",
            reverse_grade="A",
            combined_grade="A",
            specificity_score=95.0
        )
        assert isinstance(result, str)
    
    def test_format_primer_alignment_function(self):
        """Should format primer alignment using convenience function."""
        from primerlab.core.report.alignment_view import format_primer_alignment
        
        result = format_primer_alignment(
            primer_seq="ATCGATCGATCGATCGATCG",
            target_seq="ATCGATCGATCGATCGATCG",
            start=100,
            end=120,
            identity=100.0
        )
        assert isinstance(result, str)
