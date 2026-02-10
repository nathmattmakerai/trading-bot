"""
Filtre calendrier: Blackout événements économiques et rollovers.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import List


class CalendarFilter:
    """
    Blackout trading lors d'événements majeurs:
    - FOMC
    - CPI
    - NFP
    - Payrolls
    - Jours de rollover futures
    
    Veille + lendemain d'événements inclus dans blackout.
    """
    
    def __init__(self, buffer_days: int = 0):
        """
        Args:
            buffer_days: Jours avant/après événement à mettre en blackout (réduit à 0 pour activité)
        """
        self.buffer_days = buffer_days
        self.blackout_events = {
            "FOMC": [],
            "CPI": [],
            "NFP": [],
            "Payrolls": [],
            "rollover": [],
        }
        self._load_calendar_events()
    
    def _load_calendar_events(self):
        """Charge tous les événements du calendrier."""
        # 2025 FOMC dates (FOMC decision day)
        self.blackout_events["FOMC"] = [
            pd.to_datetime("2025-01-29"),
            pd.to_datetime("2025-03-18"),
            pd.to_datetime("2025-05-06"),
            pd.to_datetime("2025-06-17"),
            pd.to_datetime("2025-07-29"),
            pd.to_datetime("2025-09-16"),
            pd.to_datetime("2025-11-04"),
            pd.to_datetime("2025-12-16"),
        ]
        
        # CPI (mid-month)
        self.blackout_events["CPI"] = [
            pd.to_datetime("2025-01-15"),
            pd.to_datetime("2025-02-12"),
            pd.to_datetime("2025-03-12"),
            pd.to_datetime("2025-04-10"),
            pd.to_datetime("2025-05-14"),
            pd.to_datetime("2025-06-11"),
            pd.to_datetime("2025-07-10"),
            pd.to_datetime("2025-08-13"),
            pd.to_datetime("2025-09-10"),
            pd.to_datetime("2025-10-15"),
            pd.to_datetime("2025-11-12"),
            pd.to_datetime("2025-12-10"),
        ]
        
        # NFP (first Friday of month, 8:30 AM ET)
        self.blackout_events["NFP"] = [
            pd.to_datetime("2025-01-10"),
            pd.to_datetime("2025-02-07"),
            pd.to_datetime("2025-03-07"),
            pd.to_datetime("2025-04-04"),
            pd.to_datetime("2025-05-02"),
            pd.to_datetime("2025-06-06"),
            pd.to_datetime("2025-07-11"),
            pd.to_datetime("2025-08-08"),
            pd.to_datetime("2025-09-05"),
            pd.to_datetime("2025-10-03"),
            pd.to_datetime("2025-11-07"),
            pd.to_datetime("2025-12-05"),
        ]
        
        # Payrolls = NFP (same dates)
        self.blackout_events["Payrolls"] = self.blackout_events["NFP"].copy()
        
        # Futures rollover (3rd Friday of month)
        self.blackout_events["rollover"] = [
            pd.to_datetime("2025-01-17"),
            pd.to_datetime("2025-02-21"),
            pd.to_datetime("2025-03-21"),
            pd.to_datetime("2025-04-18"),
            pd.to_datetime("2025-05-16"),
            pd.to_datetime("2025-06-20"),
            pd.to_datetime("2025-07-18"),
            pd.to_datetime("2025-08-15"),
            pd.to_datetime("2025-09-19"),
            pd.to_datetime("2025-10-17"),
            pd.to_datetime("2025-11-21"),
            pd.to_datetime("2025-12-19"),
        ]
    
    def is_blackout_date(self, date: pd.Timestamp) -> bool:
        """
        Vérifie si date est en période de blackout.
        
        Args:
            date: pd.Timestamp à vérifier
        
        Returns:
            True si date en blackout
        """
        date_only = pd.Timestamp(date.date())
        
        for event_type, event_dates in self.blackout_events.items():
            for event_date in event_dates:
                event_date_only = pd.Timestamp(event_date.date())
                days_diff = abs((date_only - event_date_only).days)
                
                if days_diff <= self.buffer_days:
                    return True
        
        return False
    
    def get_blackout_reason(self, date: pd.Timestamp) -> str:
        """
        Retourne la raison du blackout si date est bloquée.
        
        Args:
            date: pd.Timestamp à vérifier
        
        Returns:
            Raison du blackout ou "no_blackout"
        """
        date_only = pd.Timestamp(date.date())
        
        for event_type, event_dates in self.blackout_events.items():
            for event_date in event_dates:
                event_date_only = pd.Timestamp(event_date.date())
                days_diff = abs((date_only - event_date_only).days)
                
                if days_diff <= self.buffer_days:
                    if days_diff == 0:
                        return f"{event_type}_event"
                    elif days_diff == 1:
                        return f"{event_type}_buffer"
        
        return "no_blackout"
    
    def trading_allowed(self, date: pd.Timestamp) -> bool:
        """Trading autorisé = NOT blackout."""
        return not self.is_blackout_date(date)
