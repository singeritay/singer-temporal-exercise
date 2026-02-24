from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError
import yaml

from .environment_manager import get_environment

ConfigType = TypeVar("ConfigType", bound=BaseModel)


class ConfigurationLoader:
    def __init__(self, configuration_file_name: str | Path):
        self.configuration_file_path = Path(configuration_file_name)

    def load(self, environment: str, config_model: type[ConfigType]) -> ConfigType:
        if not issubclass(config_model, BaseModel):
            raise TypeError("config_model must be a pydantic BaseModel type")

        with self.configuration_file_path.open("r", encoding="utf-8") as file:
            all_configs = yaml.safe_load(file) or {}

        if not isinstance(all_configs, dict):
            raise ValueError("Invalid config file format: top-level YAML value must be a mapping")

        environment_config = all_configs.get(environment)
        if not isinstance(environment_config, dict):
            raise ValueError(f"Missing or invalid configuration section '{environment}'")

        try:
            return config_model.model_validate(environment_config)
        except ValidationError as exc:
            raise ValueError(
                f"Missing or invalid required configuration values for '{environment}'"
            ) from exc

    def load_for_current_env(self, config_model: type[ConfigType]) -> ConfigType:
        environment = get_environment()
        return self.load(environment, config_model)
