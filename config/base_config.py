from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConfig(ABC):
    """
    Abstract base class for all bot configurations.
    Ensures consistency across versions.
    """

    @property
    @abstractmethod
    def VERSION(self) -> str:
        pass

    @property
    @abstractmethod
    def LOCKED(self) -> bool:
        pass

    @property
    @abstractmethod
    def INSTRUMENTS(self) -> list[str]:
        pass

    @property
    @abstractmethod
    def COMPRESSION_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def RISK_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def MACRO_FILTER_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def CALENDAR_FILTER_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def POSITION_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def SESSION_CONFIG(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def CONCURRENT_RULES(self) -> Dict[str, Any]:
        pass

    @property
    @abstractmethod
    def TARGET_KPI(self) -> Dict[str, Any]:
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Converts the configuration to a dictionary for easy serialization/inspection."""
        return {
            "VERSION": self.VERSION,
            "LOCKED": self.LOCKED,
            "INSTRUMENTS": self.INSTRUMENTS,
            "COMPRESSION_CONFIG": self.COMPRESSION_CONFIG,
            "RISK_CONFIG": self.RISK_CONFIG,
            "MACRO_FILTER_CONFIG": self.MACRO_FILTER_CONFIG,
            "CALENDAR_FILTER_CONFIG": self.CALENDAR_FILTER_CONFIG,
            "POSITION_CONFIG": self.POSITION_CONFIG,
            "SESSION_CONFIG": self.SESSION_CONFIG,
            "CONCURRENT_RULES": self.CONCURRENT_RULES,
            "TARGET_KPI": self.TARGET_KPI,
        }
