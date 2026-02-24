import os

DEFAULT_ENVIRONMENT = "development"
VALID_ENVIRONMENTS = {"development", "production", "integration", "testing"}


def get_environment() -> str:
    environment = os.getenv("ENV", DEFAULT_ENVIRONMENT).strip().lower()
    if environment not in VALID_ENVIRONMENTS:
        valid_values = ", ".join(sorted(VALID_ENVIRONMENTS))
        raise ValueError(f"Invalid ENV value '{environment}'. Expected one of: {valid_values}")
    return environment
