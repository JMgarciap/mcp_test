import logging
import os
import sys

def setup_logging(level=logging.INFO):
    """Configures logging for the application."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)]
    )

def get_env_var(name: str, default: str = None, required: bool = False) -> str:
    """Retrieves an environment variable."""
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Environment variable {name} is required but not set.")
    return value
