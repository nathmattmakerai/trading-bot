"""
Filtre de session: RTH US uniquement (8:00 AM - 3:00 PM ET).
"""

import pandas as pd
from datetime import datetime, time


class SessionFilter:
    """
    Contrôle que trading se fait uniquement en RTH US.
    RTH = 8:00 AM - 3:00 PM ET = 13:00 - 20:00 UTC
    
    No trading en prémarché, postmarché, sessions asiatiques/euro.
    """
    
    # RTH US en UTC
    RTH_START_UTC_HOUR = 13  # 8:00 AM ET
    RTH_END_UTC_HOUR = 20  # 3:00 PM ET (fermeture RTH)
    
    # RTH US en ET (pour référence)
    RTH_START_ET = time(8, 0)
    RTH_END_ET = time(15, 0)
    
    def __init__(self):
        self.rth_start_utc = self.RTH_START_UTC_HOUR
        self.rth_end_utc = self.RTH_END_UTC_HOUR
    
    def is_rth_session(self, timestamp: pd.Timestamp) -> bool:
        """
        Vérifie si timestamp est en RTH US.
        
        Args:
            timestamp: pd.Timestamp avec timezone ou naive (assumée UTC)
        
        Returns:
            True si en RTH
        """
        # Extraire heure UTC
        if timestamp.tz is not None:
            # Convertir en UTC si timezone-aware
            ts_utc = timestamp.tz_convert('UTC')
            hour_utc = ts_utc.hour
        else:
            # Assumer UTC si naive
            hour_utc = timestamp.hour
        
        # RTH = 13:00 - 20:00 UTC
        # Note: 20:00 = fermeture, donc on inclut jusqu'à 19:59
        return self.rth_start_utc <= hour_utc < self.rth_end_utc
    
    def is_trading_allowed(self, timestamp: pd.Timestamp) -> bool:
        """Trading autorisé = est en RTH."""
        return self.is_rth_session(timestamp)
    
    def get_session_info(self, timestamp: pd.Timestamp) -> dict:
        """
        Retourne informations sur session actuelle.
        
        Returns:
            Dict avec is_rth, session_type, hours_until_close, etc.
        """
        hour_utc = timestamp.hour
        
        if self.is_rth_session(timestamp):
            hours_until_rth_close = self.rth_end_utc - hour_utc
            session_type = "RTH"
            trading_allowed = True
        elif hour_utc < self.rth_start_utc:
            hours_until_rth_open = self.rth_start_utc - hour_utc
            session_type = "pre-market"
            trading_allowed = False
        else:
            hours_until_rth_open = 24 - hour_utc + self.rth_start_utc
            session_type = "post-market"
            trading_allowed = False
        
        return {
            "session_type": session_type,
            "trading_allowed": trading_allowed,
            "timestamp_utc_hour": hour_utc,
        }
