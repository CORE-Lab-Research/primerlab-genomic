"""
PrimerLab Exception Classes

All exceptions follow the error code format defined in error-codes.md:
    ERR_<CATEGORY>_<NUMBER>

Categories:
    SEQ → Sequence / Input errors
    CONFIG → Configuration file issues
    TOOL → External tool or dependency failures
    QC → Quality control failure
    WORKFLOW → Workflow execution errors
    IO → File read/write errors
    INTERNAL → Unexpected internal errors
    VALIDATION → Constraint violation or value mismatch
"""


class PrimerLabException(Exception):
    """Base exception for all PrimerLab errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(f"{error_code}: {message}" if error_code else message)
        self.error_code = error_code
        self.message = message
        self.details = details or {}
    
    def __str__(self):
        if self.error_code:
            return f"{self.error_code}: {self.message}"
        return self.message


class ConfigError(PrimerLabException):
    """
    Raised when configuration is invalid or missing.
    
    Error codes: ERR_CONFIG_001 to ERR_CONFIG_008
    """
    pass


class SequenceError(PrimerLabException):
    """
    Raised when input sequence is invalid.
    
    Error codes: ERR_SEQ_001 to ERR_SEQ_008
    """
    pass


class ToolExecutionError(PrimerLabException):
    """
    Raised when an external tool (Primer3, BLAST, ViennaRNA) fails.
    
    Error codes: ERR_TOOL_001 to ERR_TOOL_008
    """
    pass


class WorkflowError(PrimerLabException):
    """
    Raised when a workflow logic fails.
    
    Error codes: ERR_WORKFLOW_001 to ERR_WORKFLOW_005
    """
    pass


class QCError(PrimerLabException):
    """
    Raised when a quality control check fails (hard failure).
    
    Error codes: ERR_QC_001 to ERR_QC_008
    Note: Soft QC warnings use logger instead.
    """
    pass


class IOError(PrimerLabException):
    """
    Raised when file read/write operations fail.
    
    Error codes: ERR_IO_001 to ERR_IO_005
    Note: Named IOError to shadow Python's built-in (as per error-codes.md spec).
    """
    pass


class ValidationError(PrimerLabException):
    """
    Raised when constraint validation or value mismatch occurs.
    
    Error codes: ERR_VALIDATION_001 to ERR_VALIDATION_004
    """
    pass


class InternalError(PrimerLabException):
    """
    Raised for unexpected internal errors.
    
    Error codes: ERR_INTERNAL_001 to ERR_INTERNAL_003
    Reserved for assertion failures and unexpected states.
    """
    pass
