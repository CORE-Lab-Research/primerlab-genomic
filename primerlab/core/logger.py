"""
PrimerLab Logging System

Per blueprint-logging-system.md:
- Format: [YYYY-MM-DD HH:MM:SS][LEVEL] message
- Supports workflow context prefix: [PCR], [qPCR], [CRISPR]
- Two-phase initialization (buffer before output dir known)
"""

import logging
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Global console for rich output
console = Console()

# Current workflow context (set by workflows)
_workflow_context: Optional[str] = None


def set_workflow_context(context: str):
    """Set the current workflow context for log messages."""
    global _workflow_context
    _workflow_context = context.upper()


def clear_workflow_context():
    """Clear the workflow context."""
    global _workflow_context
    _workflow_context = None


class WorkflowContextFormatter(logging.Formatter):
    """
    Custom formatter that includes workflow context.
    
    Format: [YYYY-MM-DD HH:MM:SS][LEVEL] [CONTEXT] message
    Per blueprint-logging-system.md spec.
    """
    
    def format(self, record):
        # Get workflow context if set
        global _workflow_context
        context = f"[{_workflow_context}] " if _workflow_context else ""
        
        # Format timestamp per spec
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = record.levelname
        
        return f"[{timestamp}][{level}] {context}{record.getMessage()}"


class FileFormatter(logging.Formatter):
    """
    File formatter per blueprint-logging-system.md spec.
    
    Format: [YYYY-MM-DD HH:MM:SS][LEVEL] message
    """
    
    def format(self, record):
        global _workflow_context
        context = f"[{_workflow_context}] " if _workflow_context else ""
        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        level = record.levelname
        return f"[{timestamp}][{level}] {context}{record.getMessage()}"


def setup_logger(name="primerlab", log_file=None, level=logging.INFO):
    """
    Sets up a logger with RichHandler for console and FileHandler for file logs.
    
    Per blueprint-logging-system.md:
    - Unified logger used throughout the system
    - Supports two-phase initialization
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers to avoid duplicates
    logger.handlers = []

    # Console Handler (Rich)
    rich_handler = RichHandler(console=console, show_time=True, show_path=False)
    rich_handler.setLevel(level)
    formatter = logging.Formatter("%(message)s")
    rich_handler.setFormatter(formatter)
    logger.addHandler(rich_handler)

    # File Handler (if log_file provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)  # Always log debug to file
        file_handler.setFormatter(FileFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name="primerlab"):
    """Get or create a logger instance."""
    return logging.getLogger(name)
