import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from primerlab.core.models import WorkflowResult
from primerlab.core.logger import get_logger
from primerlab.core.exceptions import PrimerLabException

logger = get_logger()

class OutputManager:
    """
    Handles creation of run directories and saving of results.
    """
    def __init__(self, base_dir: str, workflow_name: str):
        self.base_dir = Path(base_dir)
        self.workflow_name = workflow_name
        self.run_dir = self._create_run_dir()
        
    def _create_run_dir(self) -> Path:
        """Creates a timestamped run directory."""
        # Format: YYYYMMDD_HHMMSS_WORKFLOW (e.g., 20251127_115143_PCR)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{timestamp}_{self.workflow_name.upper()}"
        full_path = self.base_dir / run_name
        
        try:
            full_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory created: {full_path}")
            return full_path
        except Exception as e:
            raise PrimerLabException(f"Failed to create output directory: {e}")

    def save_json(self, result: WorkflowResult, filename: str = "result.json"):
        """Saves WorkflowResult to a JSON file."""
        file_path = self.run_dir / filename
        try:
            data = result.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Result saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save JSON: {e}")

    def save_debug_data(self, data: Dict[str, Any], filename: str = "debug_raw.json"):
        """Saves raw debug data."""
        debug_dir = self.run_dir / "debug"
        debug_dir.mkdir(exist_ok=True)
        
        file_path = debug_dir / filename
        try:
            with open(file_path, 'w') as f:
                # Handle non-serializable objects if necessary, but for now assume dict is clean
                json.dump(data, f, indent=2, default=str)
            logger.debug(f"Debug data saved to: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save debug data: {e}")
