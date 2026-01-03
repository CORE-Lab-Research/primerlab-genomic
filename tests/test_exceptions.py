"""
Unit tests for PrimerLab Exception Classes (v0.8.0)

Tests exception hierarchy, error codes, and proper behavior
per exception-handling.md specification.
"""

import pytest


class TestPrimerLabExceptionBase:
    """Test base PrimerLabException class."""
    
    def test_base_exception_with_message_only(self):
        """Test exception with just message."""
        from primerlab.core.exceptions import PrimerLabException
        
        exc = PrimerLabException("Test error message")
        
        assert exc.message == "Test error message"
        assert exc.error_code is None
        assert str(exc) == "Test error message"
    
    def test_base_exception_with_error_code(self):
        """Test exception with message and error code."""
        from primerlab.core.exceptions import PrimerLabException
        
        exc = PrimerLabException("Test error", error_code="ERR_TEST_001")
        
        assert exc.message == "Test error"
        assert exc.error_code == "ERR_TEST_001"
        assert str(exc) == "ERR_TEST_001: Test error"
    
    def test_base_exception_with_details(self):
        """Test exception with additional details."""
        from primerlab.core.exceptions import PrimerLabException
        
        details = {"key": "value", "count": 42}
        exc = PrimerLabException("Error with details", details=details)
        
        assert exc.details == details
        assert exc.details["key"] == "value"
    
    def test_exception_inheritance(self):
        """Test that PrimerLabException inherits from Exception."""
        from primerlab.core.exceptions import PrimerLabException
        
        exc = PrimerLabException("Test")
        assert isinstance(exc, Exception)


class TestConfigError:
    """Test ConfigError exception class."""
    
    def test_config_error_creation(self):
        """Test ConfigError instantiation."""
        from primerlab.core.exceptions import ConfigError, PrimerLabException
        
        exc = ConfigError("Invalid config", error_code="ERR_CONFIG_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_CONFIG_001"
        assert "Invalid config" in str(exc)
    
    def test_config_error_raised(self):
        """Test ConfigError can be raised and caught."""
        from primerlab.core.exceptions import ConfigError
        
        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Missing key: sequence", error_code="ERR_CONFIG_003")
        
        assert exc_info.value.error_code == "ERR_CONFIG_003"


class TestSequenceError:
    """Test SequenceError exception class."""
    
    def test_sequence_error_creation(self):
        """Test SequenceError instantiation."""
        from primerlab.core.exceptions import SequenceError, PrimerLabException
        
        exc = SequenceError("Invalid nucleotide", error_code="ERR_SEQ_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_SEQ_001"
    
    def test_sequence_error_raised(self):
        """Test SequenceError can be raised and caught."""
        from primerlab.core.exceptions import SequenceError
        
        with pytest.raises(SequenceError) as exc_info:
            raise SequenceError("Sequence too short", error_code="ERR_SEQ_002")
        
        assert "Sequence too short" in str(exc_info.value)


class TestToolExecutionError:
    """Test ToolExecutionError exception class."""
    
    def test_tool_error_creation(self):
        """Test ToolExecutionError instantiation."""
        from primerlab.core.exceptions import ToolExecutionError, PrimerLabException
        
        exc = ToolExecutionError("Primer3 failed", error_code="ERR_TOOL_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_TOOL_001"
    
    def test_tool_error_with_details(self):
        """Test ToolExecutionError with details."""
        from primerlab.core.exceptions import ToolExecutionError
        
        details = {"tool": "primer3", "exit_code": 1}
        exc = ToolExecutionError("Tool crash", error_code="ERR_TOOL_002", details=details)
        
        assert exc.details["tool"] == "primer3"
        assert exc.details["exit_code"] == 1


class TestWorkflowError:
    """Test WorkflowError exception class."""
    
    def test_workflow_error_creation(self):
        """Test WorkflowError instantiation."""
        from primerlab.core.exceptions import WorkflowError, PrimerLabException
        
        exc = WorkflowError("Workflow failed", error_code="ERR_WORKFLOW_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_WORKFLOW_001"


class TestQCError:
    """Test QCError exception class."""
    
    def test_qc_error_creation(self):
        """Test QCError instantiation."""
        from primerlab.core.exceptions import QCError, PrimerLabException
        
        exc = QCError("GC content out of range", error_code="ERR_QC_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_QC_001"


class TestIOError:
    """Test IOError exception class."""
    
    def test_io_error_creation(self):
        """Test IOError instantiation (PrimerLab version)."""
        from primerlab.core.exceptions import IOError as PrimerLabIOError
        from primerlab.core.exceptions import PrimerLabException
        
        exc = PrimerLabIOError("File not found", error_code="ERR_IO_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_IO_001"


class TestValidationError:
    """Test ValidationError exception class."""
    
    def test_validation_error_creation(self):
        """Test ValidationError instantiation."""
        from primerlab.core.exceptions import ValidationError, PrimerLabException
        
        exc = ValidationError("Invalid Tm range", error_code="ERR_VALIDATION_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_VALIDATION_001"


class TestInternalError:
    """Test InternalError exception class."""
    
    def test_internal_error_creation(self):
        """Test InternalError instantiation."""
        from primerlab.core.exceptions import InternalError, PrimerLabException
        
        exc = InternalError("Unexpected state", error_code="ERR_INTERNAL_001")
        
        assert isinstance(exc, PrimerLabException)
        assert exc.error_code == "ERR_INTERNAL_001"


class TestExceptionHierarchy:
    """Test exception hierarchy relationships."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Verify all custom exceptions inherit from PrimerLabException."""
        from primerlab.core.exceptions import (
            PrimerLabException,
            ConfigError,
            SequenceError,
            ToolExecutionError,
            WorkflowError,
            QCError,
            IOError as PrimerLabIOError,
            ValidationError,
            InternalError,
        )
        
        exception_classes = [
            ConfigError,
            SequenceError,
            ToolExecutionError,
            WorkflowError,
            QCError,
            PrimerLabIOError,
            ValidationError,
            InternalError,
        ]
        
        for exc_class in exception_classes:
            assert issubclass(exc_class, PrimerLabException), \
                f"{exc_class.__name__} should inherit from PrimerLabException"
    
    def test_catch_specific_exception(self):
        """Test catching specific exception type."""
        from primerlab.core.exceptions import ConfigError, SequenceError
        
        # Should catch ConfigError
        with pytest.raises(ConfigError):
            raise ConfigError("Config error", error_code="ERR_CONFIG_001")
        
        # Should not catch SequenceError as ConfigError
        with pytest.raises(SequenceError):
            raise SequenceError("Sequence error", error_code="ERR_SEQ_001")
    
    def test_catch_base_exception(self):
        """Test that base class catches all derived exceptions."""
        from primerlab.core.exceptions import (
            PrimerLabException,
            ConfigError,
            SequenceError,
        )
        
        # ConfigError should be caught by PrimerLabException
        try:
            raise ConfigError("Test", error_code="ERR_CONFIG_001")
        except PrimerLabException as e:
            assert e.error_code == "ERR_CONFIG_001"
        
        # SequenceError should be caught by PrimerLabException
        try:
            raise SequenceError("Test", error_code="ERR_SEQ_001")
        except PrimerLabException as e:
            assert e.error_code == "ERR_SEQ_001"


class TestErrorCodeFormat:
    """Test error code formatting conventions."""
    
    def test_error_code_format_in_string(self):
        """Test that error code appears in string representation."""
        from primerlab.core.exceptions import ConfigError
        
        exc = ConfigError("Missing field", error_code="ERR_CONFIG_005")
        exc_str = str(exc)
        
        assert "ERR_CONFIG_005" in exc_str
        assert "Missing field" in exc_str
        assert exc_str == "ERR_CONFIG_005: Missing field"
    
    def test_error_code_categories(self):
        """Test various error code category prefixes."""
        from primerlab.core.exceptions import (
            ConfigError,
            SequenceError,
            ToolExecutionError,
            QCError,
            WorkflowError,
            ValidationError,
            InternalError,
        )
        
        # Each exception type should work with its category prefix
        test_cases = [
            (ConfigError, "ERR_CONFIG_001"),
            (SequenceError, "ERR_SEQ_001"),
            (ToolExecutionError, "ERR_TOOL_001"),
            (QCError, "ERR_QC_001"),
            (WorkflowError, "ERR_WORKFLOW_001"),
            (ValidationError, "ERR_VALIDATION_001"),
            (InternalError, "ERR_INTERNAL_001"),
        ]
        
        for exc_class, code in test_cases:
            exc = exc_class(f"Test {exc_class.__name__}", error_code=code)
            assert exc.error_code == code
