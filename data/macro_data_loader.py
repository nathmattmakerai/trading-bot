"""
Macro data loaders: VIX, US10Y yield, economic calendar.
"""

import pandas as pd
from typing import Dict, Tuple

try:
    import yfinance as yf
except ImportError:
    yf = None


class MacroDataLoader:
    """Charge données macro: VIX, US 10Y yield."""
    
    def __init__(self):
        self.vix_ticker = "^VIX"
        self.us10y_ticker = "^TNX"
    
    def fetch_vix(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Récupère VIX (clôture daily).
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
        
        Returns:
            DataFrame avec colonne 'vix'
        """
        try:
            vix = yf.download(
                self.vix_ticker,
                start=start_date,
                end=end_date,
                progress=False,
            )
            
            if vix.empty:
                raise ValueError("VIX data is empty")
            
            return vix[["Close"]].rename(columns={"Close": "vix"})
        
        except Exception as e:
            raise RuntimeError(f"Erreur chargement VIX: {e}")
    
    def fetch_us10y_yield(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Récupère US 10Y yield (clôture daily).
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
        
        Returns:
            DataFrame avec colonne 'us10y_yield'
        """
        try:
            us10y = yf.download(
                self.us10y_ticker,
                start=start_date,
                end=end_date,
                progress=False,
            )
            
            if us10y.empty:
                raise ValueError("US10Y data is empty")
            
            return us10y[["Close"]].rename(columns={"Close": "us10y_yield"})
        
        except Exception as e:
            raise RuntimeError(f"Erreur chargement US10Y: {e}")
    
    def combine_macro_data(
        self,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """
        Combine VIX et US10Y yield.
        
        Args:
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
        
        Returns:
            DataFrame daily avec [vix, us10y_yield]
        """
        try:
            vix = self.fetch_vix(start_date, end_date)
            us10y = self.fetch_us10y_yield(start_date, end_date)
            
            macro = pd.concat([vix, us10y], axis=1).dropna()
            
            if macro.empty:
                raise ValueError("No macro data after combining")
            
            return macro
        
        except Exception as e:
            raise RuntimeError(f"Erreur combine macro data: {e}")
    
    def get_daily_macro_value(
        self,
        date: pd.Timestamp,
        macro_df: pd.DataFrame,
    ) -> Tuple[float, float]:
        """
        Retourne valeurs VIX + US10Y pour date donnée.
        
        Args:
            date: pd.Timestamp
            macro_df: DataFrame combiné
        
        Returns:
            Tuple (vix, us10y_yield) ou (None, None) si pas de données
        """
        try:
            date_only = pd.Timestamp(date.date())
            
            if date_only in macro_df.index:
                row = macro_df.loc[date_only]
                return row["vix"], row["us10y_yield"]
            else:
                # Fallback: forward-fill si date exacte pas disponible
                available = macro_df.index[macro_df.index <= date_only]
                if len(available) > 0:
                    row = macro_df.loc[available[-1]]
                    return row["vix"], row["us10y_yield"]
            
            return None, None
        
        except Exception as e:
            print(f"Erreur get daily macro: {e}")
            return None, None


class EconomicCalendarLoader:
    """Charge calendrier économique (wrapper pour CalendarLoader)."""
    
    def __init__(self):
        self.events_by_date = {}
        self._load_events()
    
    def _load_events(self):
        """Charge tous les événements 2025."""
        # FOMC dates
        self.events_by_date["2025-01-29"] = ("FOMC", "high")
        self.events_by_date["2025-03-18"] = ("FOMC", "high")
        self.events_by_date["2025-05-06"] = ("FOMC", "high")
        self.events_by_date["2025-06-17"] = ("FOMC", "high")
        self.events_by_date["2025-07-29"] = ("FOMC", "high")
        self.events_by_date["2025-09-16"] = ("FOMC", "high")
        self.events_by_date["2025-11-04"] = ("FOMC", "high")
        self.events_by_date["2025-12-16"] = ("FOMC", "high")
        
        # CPI dates
        for month in range(1, 13):
            date_str = f"2025-{str(month).zfill(2)}-12"
            self.events_by_date[date_str] = ("CPI", "high")
        
        # NFP dates (first Friday)
        nfp_dates = [
            "2025-01-10", "2025-02-07", "2025-03-07", "2025-04-04",
            "2025-05-02", "2025-06-06", "2025-07-11", "2025-08-08",
            "2025-09-05", "2025-10-03", "2025-11-07", "2025-12-05",
        ]
        for date_str in nfp_dates:
            self.events_by_date[date_str] = ("NFP", "high")
    
    def get_events_for_date(self, date: pd.Timestamp) -> list:
        """Retourne événements pour date donnée."""
        date_str = date.strftime("%Y-%m-%d")
        
        if date_str in self.events_by_date:
            event, importance = self.events_by_date[date_str]
            return [(event, importance)]
        
        return []
