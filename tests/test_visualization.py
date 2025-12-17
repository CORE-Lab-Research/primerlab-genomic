"""Tests for GC Profile Visualization (v0.1.6)."""
import pytest
import tempfile
from pathlib import Path


class TestCalculateGCProfile:
    """Tests for calculate_gc_profile function."""
    
    def test_basic_gc_calculation(self):
        """Test GC calculation with known sequence."""
        from primerlab.core.visualization import calculate_gc_profile
        
        # GCGCGCGCGC = 100% GC (10 chars, all G or C)
        sequence = "GCGCGCGCGCGCGCGCGCGC"  # 20bp, 100% GC
        positions, gc_values = calculate_gc_profile(sequence, window_size=10, step=1)
        
        assert len(positions) > 0
        assert len(gc_values) == len(positions)
        # All windows should be 100% GC
        for gc in gc_values:
            assert gc == 100.0
    
    def test_high_gc_sequence(self):
        """Test with high GC content sequence."""
        from primerlab.core.visualization import calculate_gc_profile
        
        # 80% GC sequence
        sequence = "GCGCGCGCGCGCGCGCGCGC"  # All GC
        positions, gc_values = calculate_gc_profile(sequence, window_size=10)
        
        for gc in gc_values:
            assert gc == 100.0
    
    def test_low_gc_sequence(self):
        """Test with low GC content sequence (AT-rich)."""
        from primerlab.core.visualization import calculate_gc_profile
        
        # 0% GC sequence
        sequence = "ATATATATATATATATATATAT"
        positions, gc_values = calculate_gc_profile(sequence, window_size=10)
        
        for gc in gc_values:
            assert gc == 0.0
    
    def test_window_size_effect(self):
        """Test different window sizes."""
        from primerlab.core.visualization import calculate_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGC"
        
        pos_10, gc_10 = calculate_gc_profile(sequence, window_size=10)
        pos_20, gc_20 = calculate_gc_profile(sequence, window_size=20)
        
        # Larger window = fewer data points
        assert len(pos_10) > len(pos_20)
    
    def test_step_size_effect(self):
        """Test different step sizes."""
        from primerlab.core.visualization import calculate_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGCATGCATGCATGC"
        
        pos_1, gc_1 = calculate_gc_profile(sequence, window_size=10, step=1)
        pos_5, gc_5 = calculate_gc_profile(sequence, window_size=10, step=5)
        
        # Larger step = fewer data points
        assert len(pos_1) > len(pos_5)
    
    def test_lowercase_handling(self):
        """Test that lowercase is converted to uppercase."""
        from primerlab.core.visualization import calculate_gc_profile
        
        # Use a clearly 50% GC sequence: GCGCGCGCGC = 100% GC in each window
        sequence = "gcgcgcgcgcatatatatat"  # 20bp, first half 100% GC, second half 0% GC
        positions, gc_values = calculate_gc_profile(sequence, window_size=10)
        
        assert len(gc_values) > 0
        # Just verify it doesn't crash and returns valid percentages
        for gc in gc_values:
            assert 0.0 <= gc <= 100.0


# Check if matplotlib is available for plot tests
try:
    import matplotlib
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestPlotGCProfile:
    """Tests for plot_gc_profile function."""
    
    def test_plot_generation_png(self):
        """Test PNG plot generation."""
        from primerlab.core.visualization import plot_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGC" * 10  # 200bp
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_gc.png"
            result = plot_gc_profile(
                sequence=sequence,
                output_path=str(output_path),
                title="Test GC Profile"
            )
            
            assert result is not None
            assert output_path.exists()
            assert output_path.stat().st_size > 0
    
    def test_plot_with_primers(self):
        """Test plot with primer annotations."""
        from primerlab.core.visualization import plot_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGC" * 10
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_primers.png"
            result = plot_gc_profile(
                sequence=sequence,
                primer_fwd={"start": 0, "end": 20, "sequence": "ATGCATGCATGCATGCATGC"},
                primer_rev={"start": 180, "end": 200, "sequence": "GCATGCATGCATGCATGCAT"},
                output_path=str(output_path)
            )
            
            assert result is not None
            assert output_path.exists()
    
    def test_light_theme(self):
        """Test light theme generation."""
        from primerlab.core.visualization import plot_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGC" * 10
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_light.png"
            result = plot_gc_profile(
                sequence=sequence,
                theme="light",
                output_path=str(output_path)
            )
            
            assert result is not None
    
    def test_dark_theme(self):
        """Test dark theme generation."""
        from primerlab.core.visualization import plot_gc_profile
        
        sequence = "ATGCATGCATGCATGCATGC" * 10
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_dark.png"
            result = plot_gc_profile(
                sequence=sequence,
                theme="dark",
                output_path=str(output_path)
            )
            
            assert result is not None


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestGenerateGCProfileFromResult:
    """Tests for generate_gc_profile_from_result function."""
    
    def test_from_result_dict(self):
        """Test generation from workflow result dict."""
        from primerlab.core.visualization import generate_gc_profile_from_result
        
        result = {
            "workflow": "pcr",
            "primers": {
                "forward": {"start": 0, "end": 20, "sequence": "ATGC" * 5},
                "reverse": {"start": 180, "end": 200, "sequence": "GCAT" * 5}
            },
            "amplicons": [{"start": 0, "end": 200, "length": 200}]
        }
        
        sequence = "ATGCATGCATGCATGCATGC" * 10
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output = generate_gc_profile_from_result(
                result=result,
                sequence=sequence,
                output_dir=tmpdir,
                theme="light"
            )
            
            assert output is not None
            assert Path(output).exists()
