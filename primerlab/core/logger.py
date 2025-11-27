import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.console import Console

# Global console for rich output
console = Console()

def setup_logger(name="primerlab", log_file=None, level=logging.INFO):
    """
    Sets up a logger with RichHandler for console and FileHandler for file logs.
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
        file_handler.setLevel(logging.DEBUG) # Always log debug to file
        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger

def get_logger(name="primerlab"):
    return logging.getLogger(name)
