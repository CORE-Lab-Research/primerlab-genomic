"""CLI Integration Tests (v0.1.3)."""
import pytest
import subprocess
import sys
from pathlib import Path


def get_output(result):
    """Combine stdout and stderr for checking."""
    return result.stdout + result.stderr


class TestCLIVersion:
    """Tests for version commands."""
    
    def test_version_flag(self):
        """--version should return version string."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "--version"],
            capture_output=True,
            text=True
        )
        assert "0.2.0" in get_output(result)
    
    def test_version_command(self):
        """version command should return version string."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "version"],
            capture_output=True,
            text=True
        )
        assert "0.2.0" in get_output(result)


class TestCLIHealth:
    """Tests for health check command."""
    
    def test_health_command(self):
        """health command should complete and show output."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "health"],
            capture_output=True,
            text=True
        )
        output = get_output(result)
        # Health check should show version and Python info regardless of deps
        assert "PrimerLab" in output or "Health" in output or "Python" in output
    
    def test_health_checks_dependencies(self):
        """health command should check key dependencies."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "health"],
            capture_output=True,
            text=True
        )
        output = get_output(result)
        # Should check for Python at minimum
        assert "Python" in output


class TestCLIInit:
    """Tests for init command."""
    
    def test_init_command_help(self):
        """init --help should show options."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "init", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = get_output(result)
        assert "--workflow" in output or "workflow" in output
        assert "--output" in output or "output" in output


class TestCLIRun:
    """Tests for run command."""
    
    def test_run_help(self):
        """run --help should show options."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = get_output(result)
        assert "pcr" in output
        assert "qpcr" in output
        assert "--config" in output


class TestCLIBatchGenerate:
    """Tests for batch-generate command."""
    
    def test_batch_generate_help(self):
        """batch-generate --help should show options."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "batch-generate", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = get_output(result)
        assert "--input" in output or "input" in output.lower()
        assert "--output" in output or "output" in output.lower()


class TestCLIExportFlag:
    """Tests for --export flag."""
    
    def test_run_export_help(self):
        """--export flag should be in run help."""
        result = subprocess.run(
            [sys.executable, "-m", "primerlab.cli.main", "run", "--help"],
            capture_output=True,
            text=True
        )
        output = get_output(result)
        assert "--export" in output
