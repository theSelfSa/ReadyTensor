# ReadyTensor/utils/config.py

"""
Configuration loading with .env support
Create and load .env file, then override with environment variables
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from multiple sources:
    1. .env file (in project root or current directory)
    2. config.json file  
    3. Environment variables (override)
    """

    # Load .env file (search in multiple locations)
    env_locations = [
        Path.cwd() / ".env",  # Current directory
        Path(__file__).parent.parent.parent / ".env",  # Project root
        Path.home() / ".env"  # User home directory
    ]

    for env_file in env_locations:
        if env_file.exists():
            load_dotenv(env_file)
            print(f"Loaded environment from: {env_file}")
            break
    else:
        print("No .env file found, using system environment variables")

    # Default configuration
    config: Dict[str, Any] = {
        "max_workers": 4,
        "token_limit": 8000,
        "assessment_level": "professional",
        "openai_model": "gpt-4o-mini"
    }

    # Load from config.json if exists
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
                print(f"Loaded config from: {config_path}")
        except Exception as e:
            print(f"Error loading config file: {e}")

    # Load from environment variables (highest priority)
    if os.getenv("OPENAI_API_KEY"):
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY")

    if os.getenv("RT_MAX_WORKERS"):
        config["max_workers"] = int(os.getenv("RT_MAX_WORKERS"))

    if os.getenv("RT_TOKEN_LIMIT"):
        config["token_limit"] = int(os.getenv("RT_TOKEN_LIMIT"))

    if os.getenv("RT_ASSESSMENT_LEVEL"):
        config["assessment_level"] = os.getenv("RT_ASSESSMENT_LEVEL")

    if os.getenv("OPENAI_MODEL"):
        config["openai_model"] = os.getenv("OPENAI_MODEL")

    # Validate required configuration
    if not config.get("openai_api_key"):
        raise ValueError(
            "OpenAI API key is required. Set OPENAI_API_KEY in .env file or environment variable"
        )

    return config


def create_env_file(api_key: str, config_overrides: Dict[str, Any] = None) -> None:
    """
    Create .env file with user configuration.
    Uses default values if config_overrides is not provided.
    """

    if config_overrides is None:
        config_overrides = {}

    max_workers = config_overrides.get('max_workers', 4)
    token_limit = config_overrides.get('token_limit', 8000)
    assessment_level = config_overrides.get('assessment_level', 'professional')
    openai_model = config_overrides.get('openai_model', 'gpt-4o-mini')

    env_content = f"""# ReadyTensor Configuration

# OpenAI Configuration
OPENAI_API_KEY={api_key}

# Assessment Configuration
RT_MAX_WORKERS={max_workers}
RT_TOKEN_LIMIT={token_limit}
RT_ASSESSMENT_LEVEL={assessment_level}

# Model Configuration
OPENAI_MODEL={openai_model}
"""

    env_path = Path.cwd() / ".env"
    with open(env_path, 'w') as f:
        f.write(env_content)

    print(f"Configuration saved to: {env_path}")
