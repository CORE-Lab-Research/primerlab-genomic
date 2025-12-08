import yaml
import copy
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import ConfigError
from .logger import get_logger

logger = get_logger()

def load_yaml(path: str) -> Dict[str, Any]:
    """Loads a YAML file safely."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}", "ERR_CONFIG_001")
    except yaml.YAMLError as e:
        raise ConfigError(f"Invalid YAML syntax in {path}: {e}", "ERR_CONFIG_002")

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merges two dictionaries.
    - Dicts are merged.
    - Lists and scalars in 'override' replace 'base'.
    """
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result

def validate_config(config: Dict[str, Any]):
    """
    Validates the merged configuration against required schema.
    Provides clear, actionable error messages.
    """
    # Check required top-level sections
    required_keys = ["workflow", "input", "parameters", "output"]
    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ConfigError(
            f"Missing required config section(s): {', '.join(missing_keys)}. "
            f"Your config must include: {', '.join(required_keys)}",
            "ERR_CONFIG_003"
        )
            
    # Validate workflow name
    workflow = config.get("workflow")
    if not workflow:
        raise ConfigError(
            "Workflow name cannot be empty. "
            "Please specify 'workflow: pcr' or 'workflow: qpcr' in your config.",
            "ERR_CONFIG_004"
        )
    
    # Check for valid workflow types
    valid_workflows = ["pcr", "qpcr"]
    if workflow.lower() not in valid_workflows:
        raise ConfigError(
            f"Unknown workflow '{workflow}'. "
            f"Valid workflows are: {', '.join(valid_workflows)}",
            "ERR_CONFIG_007"
        )

    # Validate input section
    input_section = config.get("input", {})
    if not input_section.get("sequence"):
        raise ConfigError(
            "Input sequence is missing. "
            "Add 'input: sequence: <your_sequence>' or 'input: sequence: path/to/file.fasta'",
            "ERR_CONFIG_008"
        )

    # Validate output directory
    output_section = config.get("output", {})
    if not output_section.get("directory"):
        raise ConfigError(
            "Output directory must be specified. "
            "Add 'output: directory: <output_folder>' to your config.",
            "ERR_CONFIG_005"
        )
    
    # Validate parameter ranges (optional but helpful)
    params = config.get("parameters", {})
    
    # Check Tm range validity
    tm = params.get("tm", {})
    if tm:
        tm_min = tm.get("min", 0)
        tm_max = tm.get("max", 100)
        if tm_min >= tm_max:
            raise ConfigError(
                f"Invalid Tm range: min ({tm_min}) must be less than max ({tm_max}).",
                "ERR_CONFIG_009"
            )
    
    # Check product_size range validity
    p_size = params.get("product_size", {})
    if p_size:
        p_min = p_size.get("min", 0)
        p_max = p_size.get("max", 10000)
        if p_min >= p_max:
            raise ConfigError(
                f"Invalid product_size range: min ({p_min}) must be less than max ({p_max}).",
                "ERR_CONFIG_010"
            )

def load_and_merge_config(workflow: str, user_config_path: Optional[str] = None, cli_overrides: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main entry point for config loading.
    1. Load default config for the workflow.
    2. Load user config (if provided).
    3. Apply CLI overrides.
    4. Validate.
    """
    # 1. Load Default Config
    # Assuming default configs are in primerlab/config/<workflow>_default.yaml
    base_path = Path(__file__).parent.parent / "config" / f"{workflow}_default.yaml"
    
    if not base_path.exists():
        raise ConfigError(f"Default config for workflow '{workflow}' not found at {base_path}", "ERR_CONFIG_006")
        
    logger.debug(f"Loading default config from {base_path}")
    final_config = load_yaml(str(base_path))

    # 2. Load User Config
    if user_config_path:
        logger.info(f"Loading user config from {user_config_path}")
        user_config = load_yaml(user_config_path)
        final_config = deep_merge(final_config, user_config)

    # 3. Apply CLI Overrides
    if cli_overrides:
        logger.debug("Applying CLI overrides")
        final_config = deep_merge(final_config, cli_overrides)

    # 4. Process Enhancements (Presets & Product Size)
    final_config = _process_enhancements(final_config)

    # 5. Validate
    validate_config(final_config)
    
    return final_config

def _process_enhancements(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies v0.1.1+ enhancements:
    1. Presets (e.g., preset: "long_range", "dna_barcoding", "rt_pcr")
    2. product_size (min/opt/max) -> product_size_range
    """
    params = config.get("parameters", {})
    
    # 1. Presets - v0.1.3: Load from YAML files or use inline defaults
    preset = config.get("preset")
    if preset:
        logger.info(f"Applying preset: {preset}")
        
        # Try to load preset from file first
        preset_file = Path(__file__).parent.parent / "config" / f"{preset}_default.yaml"
        
        if preset_file.exists():
            preset_config = load_yaml(str(preset_file))
            # Merge preset params with current params (user params override preset)
            preset_params = preset_config.get("parameters", {})
            for key, value in preset_params.items():
                if key not in params:
                    params[key] = value
            # Also merge QC settings if not already set
            preset_qc = preset_config.get("qc", {})
            if preset_qc and "qc" not in config:
                config["qc"] = preset_qc
            logger.debug(f"Loaded preset from {preset_file}")
        else:
            # Fallback to inline presets for backward compatibility
            if preset == "long_range":
                params.setdefault("product_size", {"min": 1000, "opt": 2000, "max": 3000})
                params.setdefault("tm", {"min": 60.0, "opt": 62.0, "max": 65.0})
            elif preset == "standard_pcr":
                params.setdefault("product_size", {"min": 100, "opt": 200, "max": 600})
            elif preset == "dna_barcoding":
                params.setdefault("product_size", {"min": 400, "opt": 550, "max": 700})
                params.setdefault("tm", {"min": 50.0, "opt": 55.0, "max": 60.0})
            elif preset == "rt_pcr":
                params.setdefault("product_size", {"min": 80, "opt": 130, "max": 200})
                params.setdefault("tm", {"min": 58.0, "opt": 60.0, "max": 62.0})
            logger.debug(f"Applied inline preset: {preset}")
        
    # 2. product_size -> product_size_range
    # Primer3 expects [[min, max]] for PRIMER_PRODUCT_SIZE_RANGE
    # We support user-friendly product_size: {min: X, opt: Y, max: Z}
    
    p_size = params.get("product_size")
    p_range = params.get("product_size_range")
    
    if p_size and not p_range:
        # Convert user-friendly size to range format
        # Note: Primer3 takes a list of ranges. We use min-max.
        min_s = p_size.get("min", 100)
        max_s = p_size.get("max", 300)
        params["product_size_range"] = [[min_s, max_s]]
        logger.debug(f"Converted product_size {p_size} to range [[{min_s}, {max_s}]]")
        
    return config
