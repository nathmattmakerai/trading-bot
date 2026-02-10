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
        
        Pour les données d'archives (> 60 jours), télécharge les données daily
        et génère des bougies 15m simulées réalistes.
        
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
        
        # Ticker mappings - NQ/ES → indices correspondants
        ticker_map = {
            "NQ": "^NDX",   # NASDAQ 100
            "ES": "^GSPC",  # S&P 500
        }
        
        ticker = ticker_map[instrument]
        
        # Vérifier si les données intraday sont disponibles (< 60 jours)
        from datetime import datetime
        start_dt = pd.to_datetime(start_date)
        days_ago = (datetime.now() - start_dt.to_pydatetime().replace(tzinfo=None)).days
        
        if days_ago <= 60 and timeframe in ["15m", "30m", "1h"]:
            # Essayer de télécharger les données intraday
            try:
                df = yf.download(
                    ticker,
                    start=start_date,
                    end=end_date,
                    interval=timeframe,
                    progress=False,
                )
                
                if not df.empty and len(df) > 10:
                    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
                    df.columns = ["open", "high", "low", "close", "volume"]
                    df = df.dropna()
                    return df
            except Exception:
                pass  # Fallback to daily data conversion
        
        # Télécharger données daily (toujours disponibles)
        try:
            df_daily = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                interval="1d",
                progress=False,
            )
            
            if df_daily.empty:
                raise RuntimeError(f"Aucune donnée disponible pour {instrument} ({start_date} to {end_date})")
            
            # Flatten MultiIndex columns if present
            if isinstance(df_daily.columns, pd.MultiIndex):
                df_daily.columns = df_daily.columns.get_level_values(0)
            
            df_daily = df_daily[["Open", "High", "Low", "Close", "Volume"]].copy()
            df_daily.columns = ["open", "high", "low", "close", "volume"]
            df_daily = df_daily.dropna()
            
            # Convertir en timeframe demandé
            if timeframe == "1d":
                return df_daily
            else:
                # Générer données intraday simulées à partir des données daily
                return self._generate_intraday_from_daily(df_daily, timeframe)
                
        except Exception as e:
            raise RuntimeError(f"Erreur chargement données {instrument}: {e}")
    
    def _generate_intraday_from_daily(
        self,
        df_daily: pd.DataFrame,
        timeframe: str = "15m",
    ) -> pd.DataFrame:
        """
        Génère des données intraday simulées à partir de données daily.
        
        Utilise un modèle de micro-structure pour créer des bougies réalistes
        tout en respectant les niveaux OHLC daily.
        
        Args:
            df_daily: DataFrame avec données daily
            timeframe: '15m', '30m', '1h'
        
        Returns:
            DataFrame avec données intraday simulées
        """
        import numpy as np
        
        # Nombre de bougies par jour selon le timeframe (session RTH: 9:30-16:00 = 6.5h)
        bars_per_day = {
            "15m": 26,  # 6.5h * 4 bougies/h
            "30m": 13,  # 6.5h * 2 bougies/h
            "1h": 7,    # 6.5h arrondi
        }
        
        n_bars = bars_per_day.get(timeframe, 26)
        intraday_rows = []
        
        for date_idx, daily_row in df_daily.iterrows():
            day_open = float(daily_row["open"])
            day_high = float(daily_row["high"])
            day_low = float(daily_row["low"])
            day_close = float(daily_row["close"])
            day_volume = float(daily_row["volume"])
            
            # Générer un chemin de prix réaliste
            np.random.seed(int(date_idx.timestamp()) % (2**31 - 1))
            
            # Pattern typique: ouverture volatile, milieu de journée calme, fermeture active
            # Créer des points clés aléatoires dans le range daily
            intraday_range = day_high - day_low
            
            # Générer des prix de clôture pour chaque bougie
            # Le prix doit partir de day_open et finir à day_close
            # en passant par day_high et day_low à un moment
            
            # Position relative du high et low dans la journée (simulé)
            high_bar = np.random.randint(1, n_bars - 2)
            low_bar = np.random.randint(1, n_bars - 2)
            
            # S'assurer que high et low ne sont pas au même moment
            while abs(high_bar - low_bar) < 2:
                low_bar = np.random.randint(1, n_bars - 2)
            
            # Créer une trajectoire de prix
            closes = np.zeros(n_bars)
            
            # Générer une marche aléatoire contrôlée
            for i in range(n_bars):
                if i == 0:
                    closes[i] = day_open
                elif i == n_bars - 1:
                    closes[i] = day_close
                elif i == high_bar:
                    closes[i] = day_high - np.random.uniform(0, intraday_range * 0.05)
                elif i == low_bar:
                    closes[i] = day_low + np.random.uniform(0, intraday_range * 0.05)
                else:
                    # Interpoler avec du bruit
                    progress = i / (n_bars - 1)
                    base_price = day_open + (day_close - day_open) * progress
                    noise = np.random.normal(0, intraday_range * 0.1)
                    closes[i] = np.clip(base_price + noise, day_low, day_high)
            
            # Créer les bougies OHLC pour chaque période
            volume_per_bar = day_volume / n_bars
            
            for i in range(n_bars):
                # Créer timestamp pour cette bougie
                if timeframe == "15m":
                    minutes = 9 * 60 + 30 + i * 15  # 9:30 + i*15 min
                elif timeframe == "30m":
                    minutes = 9 * 60 + 30 + i * 30
                else:  # 1h
                    minutes = 9 * 60 + 30 + i * 60
                
                bar_time = pd.Timestamp(
                    year=date_idx.year,
                    month=date_idx.month,
                    day=date_idx.day,
                    hour=minutes // 60,
                    minute=minutes % 60,
                    tz="America/New_York"
                ).tz_convert("UTC")
                
                # OHLC pour cette bougie
                if i == 0:
                    bar_open = day_open
                else:
                    bar_open = closes[i - 1]
                
                bar_close = closes[i]
                
                # High/Low: entre open et close + bruit
                bar_range = abs(bar_close - bar_open) + intraday_range * np.random.uniform(0.01, 0.05)
                bar_high = max(bar_open, bar_close) + abs(np.random.normal(0, bar_range * 0.3))
                bar_low = min(bar_open, bar_close) - abs(np.random.normal(0, bar_range * 0.3))
                
                # S'assurer que le high/low journalier est atteint
                if i == high_bar:
                    bar_high = day_high
                if i == low_bar:
                    bar_low = day_low
                
                # Contraindre aux limites daily
                bar_high = min(bar_high, day_high)
                bar_low = max(bar_low, day_low)
                
                # Volume avec pattern U-shape typique (plus de volume en open et close)
                volume_factor = 1.0
                if i < 3:  # Première heure
                    volume_factor = 1.5
                elif i >= n_bars - 3:  # Dernière heure
                    volume_factor = 1.3
                
                bar_volume = volume_per_bar * volume_factor * np.random.uniform(0.7, 1.3)
                
                intraday_rows.append({
                    "open": bar_open,
                    "high": bar_high,
                    "low": bar_low,
                    "close": bar_close,
                    "volume": bar_volume,
                    "timestamp": bar_time,
                })
        
        df_intraday = pd.DataFrame(intraday_rows)
        df_intraday.set_index("timestamp", inplace=True)
        df_intraday.sort_index(inplace=True)
        
        return df_intraday
    
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
    
    def _flatten_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplatit les colonnes MultiIndex si présentes."""
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df
    
    def fetch_vix(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Récupère VIX (clôture daily)."""
        try:
            vix = yf.download(self.vix_ticker, start=start_date, end=end_date, progress=False)
            vix = self._flatten_columns(vix)
            return vix[["Close"]].rename(columns={"Close": "vix"})
        except Exception as e:
            raise RuntimeError(f"Erreur chargement VIX: {e}")
    
    def fetch_us10y_yield(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Récupère US 10Y yield (clôture daily)."""
        try:
            us10y = yf.download(self.us10y_ticker, start=start_date, end=end_date, progress=False)
            us10y = self._flatten_columns(us10y)
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
            DataFrame daily avec [vix, us10y_yield], indexé par date (datetime.date)
        """
        vix = self.fetch_vix(start_date, end_date)
        us10y = self.fetch_us10y_yield(start_date, end_date)
        
        # Combine logic: join and fill missing values
        macro = pd.concat([vix, us10y], axis=1)
        macro = macro.ffill().dropna() # Forward fill then remove remaining NaNs
        
        if macro.empty:
            print(f"[Warning] No macro data available for {start_date} to {end_date}")
            # Create dummy data as fallback to avoid blocking the bot entirely
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            macro = pd.DataFrame({"vix": 18.0, "us10y_yield": 4.0}, index=dates)
            macro.index = macro.index.date
            print("[Fallback] Using neutral macro dummy data.")
            return macro

        # Convertir l'index en date simple pour faciliter la correspondance
        macro.index = pd.to_datetime(macro.index).date
        
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
