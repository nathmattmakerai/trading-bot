from typing import Type, Union
from config.base_config import BaseConfig
from config.rules_v1 import RulesV1
from config.rules_v2 import RulesV2

class ConfigManager:
    """
    Manages loading and switching between different versions of the bot configuration.
    """

    _CONFIG_MAP = {
        "v1": RulesV1,
        "v2": RulesV2
    }

    @staticmethod
    def get_config(version: str = "v1") -> BaseConfig:
        """
        Returns the requested configuration instance.

        Args:
            version: 'v1' or 'v2'

        Returns:
            An instance of BaseConfig (RulesV1 or RulesV2)
        """
        config_class = ConfigManager._CONFIG_MAP.get(version.lower())
        if not config_class:
            raise ValueError(f"Unsupported configuration version: {version}. Supported: {list(ConfigManager._CONFIG_MAP.keys())}")

        return config_class()

    @staticmethod
    def list_available_versions() -> list[str]:
        """Returns a list of available configuration versions."""
        return list(ConfigManager._CONFIG_MAP.keys())

# Singleton instance for easy access if preferred
# (Though static methods are generally cleaner for this use case)
manager = ConfigManager()
