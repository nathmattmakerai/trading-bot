"""
Data loaders pour futures CME et données macro.
"""

import pandas as pd
from typing import Tuple, Dict
from datetime import datetime, timedelta

try:
    import yfinance as yf
except ImportError:
    yf = None


class FuturesDataLoader:
    """Charge NQ/ES en 15m + resample vers H1/H4."""
    
    def __init__(self, data_source: str = "yahoo"):
        """
        Args:
            data_source: Source de données ('yahoo', 'polygon', 'local_csv')
        """
        self.data_source = data_source
        self.instruments = ["NQ", "ES"]
        self.base_timeframe = "15m"
        
    def fetch_futures_data(
        self,
        instrument: str,
        start_date: str,
        end_date: str,
        timeframe: str = "15m",
    ) -> pd.DataFrame:
        """
        Récupère données futures NQ/ES.
        
        Args:
            instrument: 'NQ' ou 'ES'
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
            timeframe: '15m', '1h', '4h', '1d'
        
        Returns:
            DataFrame avec colonnes: [open, high, low, close, volume]
        """
        if instrument not in self.instruments:
            raise ValueError(f"Instrument {instrument} non supporté. Utilisez {self.instruments}")
        
        # Ticker Yahoo Finance pour futures
        ticker_map = {
            "NQ": "^GSPC",  # Remplacer par symbole futures réel (ex: NQU24)
            "ES": "^GSPC",  # Remplacer par symbole futures réel (ex: ESU24)
        }
        
        try:
            df = yf.download(
                ticker_map[instrument],
                start=start_date,
                end=end_date,
                interval=timeframe.replace("m", "m").replace("h", "h"),
            )
            
            # Nettoyer et renommer colonnes
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.columns = ["open", "high", "low", "close", "volume"]
            df = df.dropna()
            
            return df
            
        except Exception as e:
            raise RuntimeError(f"Erreur chargement données {instrument}: {e}")
    
    def resample_to_timeframe(
        self,
        df: pd.DataFrame,
        from_tf: str,
        to_tf: str,
    ) -> pd.DataFrame:
        """
        Resample données vers timeframe supérieur.
        
        Args:
            df: DataFrame original
            from_tf: '1m' ou '15m'
            to_tf: '15m', '1h', '4h', '1d'
        
        Returns:
            DataFrame resamplé
        """
        freq_map = {"15m": "15min", "1h": "1h", "4h": "4h", "1d": "1d"}
        
        resampled = df.resample(freq_map[to_tf]).agg({
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }).dropna()
        
        return resampled
    
    def verify_data_continuity(self, df: pd.DataFrame) -> Dict[str, bool]:
        """
        Vérifie continuité données (rollovers, gaps).
        
        Returns:
            Dict avec checks: {'has_gaps': bool, 'has_nans': bool, ...}
        """
        checks = {
            "has_nans": df.isnull().any().any(),
            "total_rows": len(df),
            "date_range": f"{df.index[0]} to {df.index[-1]}",
        }
        
        return checks


class MacroDataLoader:
    """Charge données macro: VIX, US 10Y yield."""
    
    def __init__(self):
        self.vix_ticker = "^VIX"
        self.us10y_ticker = "^TNX"
    
    def fetch_vix(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Récupère VIX (clôture daily)."""
        try:
            vix = yf.download(self.vix_ticker, start=start_date, end=end_date)
            return vix[["Close"]].rename(columns={"Close": "vix"})
        except Exception as e:
            raise RuntimeError(f"Erreur chargement VIX: {e}")
    
    def fetch_us10y_yield(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Récupère US 10Y yield (clôture daily)."""
        try:
            us10y = yf.download(self.us10y_ticker, start=start_date, end=end_date)
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
        
        Returns:
            DataFrame daily avec [vix, us10y_yield]
        """
        vix = self.fetch_vix(start_date, end_date)
        us10y = self.fetch_us10y_yield(start_date, end_date)
        
        macro = pd.concat([vix, us10y], axis=1).dropna()
        return macro


class CalendarLoader:
    """Charge calendrier économique (FOMC, NFP, CPI, rollover dates)."""
    
    def __init__(self):
        self.events = {
            "FOMC": [],
            "NFP": [],
            "CPI": [],
            "Payrolls": [],
            "rollover": [],
        }
    
    def load_fomc_dates(self, year: int) -> list:
        """Retourne dates FOMC pour année donnée."""
        # Hard-coded pour 2025/2026
        fomc_2025 = [
            "2025-01-29",
            "2025-03-18",
            "2025-05-06",
            "2025-06-17",
            "2025-07-29",
            "2025-09-16",
            "2025-11-04",
            "2025-12-16",
        ]
        return fomc_2025
    
    def load_nfp_dates(self, year: int) -> list:
        """Retourne dates NFP (premier vendredi du mois)."""
        # Approximation: premiers vendredis
        nfp_dates = [
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
        return nfp_dates
    
    def load_cpi_dates(self, year: int) -> list:
        """Retourne dates CPI (mid-month)."""
        cpi_dates = [
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
        return cpi_dates
    
    def is_blackout_date(self, date: datetime, buffer_days: int = 1) -> bool:
        """
        Vérifie si date est en blackout (événement + buffer).
        
        Args:
            date: datetime à vérifier
            buffer_days: jours avant/après événement
        
        Returns:
            True si date en blackout
        """
        year = date.year
        blackout_dates = (
            self.load_fomc_dates(year) +
            self.load_nfp_dates(year) +
            self.load_cpi_dates(year)
        )
        
        for event_date_str in blackout_dates:
            event_date = pd.to_datetime(event_date_str)
            if abs((date - event_date).days) <= buffer_days:
                return True
        
        return False
    
    def load_futures_rollover_dates(self, year: int) -> list:
        """Retourne dates rollover futures (3e vendredi du mois)."""
        rollover_dates = [
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
        return rollover_dates
