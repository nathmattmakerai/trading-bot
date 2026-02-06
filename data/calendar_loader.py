"""
Calendar loader: Événements économiques et rollovers.
"""

import pandas as pd
from typing import List, Tuple


class CalendarLoader:
    """Charge et gère calendrier économique/rollovers."""
    
    def __init__(self):
        """Initialise calendrier."""
        self.fomc_dates = self._load_fomc_dates()
        self.nfp_dates = self._load_nfp_dates()
        self.cpi_dates = self._load_cpi_dates()
        self.rollover_dates = self._load_rollover_dates()
    
    def _load_fomc_dates(self) -> List[pd.Timestamp]:
        """Charge dates FOMC 2025."""
        dates_str = [
            "2025-01-29",
            "2025-03-18",
            "2025-05-06",
            "2025-06-17",
            "2025-07-29",
            "2025-09-16",
            "2025-11-04",
            "2025-12-16",
        ]
        return [pd.to_datetime(d) for d in dates_str]
    
    def _load_nfp_dates(self) -> List[pd.Timestamp]:
        """Charge dates NFP 2025 (premier vendredi du mois)."""
        dates_str = [
            "2025-01-10",
            "2025-02-07",
            "2025-03-07",
            "2025-04-04",
            "2025-05-02",
            "2025-06-06",
            "2025-07-11",
            "2025-08-08",
            "2025-09-05",
            "2025-10-03",
            "2025-11-07",
            "2025-12-05",
        ]
        return [pd.to_datetime(d) for d in dates_str]
    
    def _load_cpi_dates(self) -> List[pd.Timestamp]:
        """Charge dates CPI 2025 (mid-month)."""
        dates_str = [
            "2025-01-15",
            "2025-02-12",
            "2025-03-12",
            "2025-04-10",
            "2025-05-14",
            "2025-06-11",
            "2025-07-10",
            "2025-08-13",
            "2025-09-10",
            "2025-10-15",
            "2025-11-12",
            "2025-12-10",
        ]
        return [pd.to_datetime(d) for d in dates_str]
    
    def _load_rollover_dates(self) -> List[pd.Timestamp]:
        """Charge dates rollover futures 2025 (3e vendredi du mois)."""
        dates_str = [
            "2025-01-17",
            "2025-02-21",
            "2025-03-21",
            "2025-04-18",
            "2025-05-16",
            "2025-06-20",
            "2025-07-18",
            "2025-08-15",
            "2025-09-19",
            "2025-10-17",
            "2025-11-21",
            "2025-12-19",
        ]
        return [pd.to_datetime(d) for d in dates_str]
    
    def is_blackout_date(
        self,
        date: pd.Timestamp,
        buffer_days: int = 1,
    ) -> bool:
        """
        Vérifie si date est en blackout (événement + buffer).
        
        Args:
            date: pd.Timestamp à vérifier
            buffer_days: Jours avant/après événement
        
        Returns:
            True si date en blackout
        """
        date_only = pd.Timestamp(date.date())
        
        all_event_dates = (
            self.fomc_dates +
            self.nfp_dates +
            self.cpi_dates +
            self.rollover_dates
        )
        
        for event_date in all_event_dates:
            event_date_only = pd.Timestamp(event_date.date())
            days_diff = abs((date_only - event_date_only).days)
            
            if days_diff <= buffer_days:
                return True
        
        return False
    
    def get_blackout_reason(self, date: pd.Timestamp) -> str:
        """
        Retourne raison du blackout si applicable.
        
        Args:
            date: pd.Timestamp à vérifier
        
        Returns:
            Raison du blackout ou "no_blackout"
        """
        date_only = pd.Timestamp(date.date())
        
        event_groups = {
            "FOMC": self.fomc_dates,
            "NFP": self.nfp_dates,
            "CPI": self.cpi_dates,
            "rollover": self.rollover_dates,
        }
        
        for event_name, event_dates in event_groups.items():
            for event_date in event_dates:
                event_date_only = pd.Timestamp(event_date.date())
                days_diff = abs((date_only - event_date_only).days)
                
                if days_diff == 0:
                    return f"{event_name}_event"
                elif days_diff == 1:
                    return f"{event_name}_buffer"
        
        return "no_blackout"
