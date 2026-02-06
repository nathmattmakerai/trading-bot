"""
Détecteur de compression: ATR-based range detection.
"""

import pandas as pd
import numpy as np


class CompressionDetector:
    """
    Détecte compression (volatilité basse) pour setup breakout.
    
    Critères:
    - ATR(14) < 0.75 × ATR(50): ATR relatif bas
    - Range(20) < 1.5 × ATR(14): Range confiné
    """
    
    def __init__(
        self,
        atr_period: int = 14,
        atr_lookback: int = 50,
        range_lookback: int = 20,
        atr_ratio_threshold: float = 0.65,
        range_ratio_threshold: float = 2.0,
    ):
        """
        Args:
            atr_period: Période ATR court terme
            atr_lookback: Période ATR long terme
            range_lookback: Nombre de bougies pour calculer range
            atr_ratio_threshold: Ratio ATR pour déterminer compression (0.65 = 35% reduction in vol)
            range_ratio_threshold: Ratio range/ATR (default 2.0)
        """
        self.atr_period = atr_period
        self.atr_lookback = atr_lookback
        self.range_lookback = range_lookback
        self.atr_ratio = atr_ratio_threshold
        self.range_ratio = range_ratio_threshold
    
    def calculate_atr(self, df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calcule Average True Range.
        
        Args:
            df: DataFrame avec colonnes [high, low, close]
            period: Période ATR
        
        Returns:
            pd.Series avec valeurs ATR
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    def calculate_range(self, df: pd.DataFrame, lookback: int) -> pd.Series:
        """
        Calcule range (high - low) sur lookback period.
        
        Args:
            df: DataFrame avec colonnes [high, low]
            lookback: Nombre de bougies
        
        Returns:
            pd.Series avec range
        """
        high = df["high"]
        low = df["low"]
        
        rolling_high = high.rolling(window=lookback).max()
        rolling_low = low.rolling(window=lookback).min()
        
        range_val = rolling_high - rolling_low
        return range_val
    
    def is_compression(self, df: pd.DataFrame) -> bool:
        """
        Vérifie si bougie courant est en compression.
        
        Args:
            df: DataFrame avec OHLCV (min 50 bougies de backtest)
        
        Returns:
            True si compression détectée
        """
        if len(df) < self.atr_lookback:
            return False
        
        # Calculer ATR court et long
        atr_short = self.calculate_atr(df, self.atr_period)
        atr_long = self.calculate_atr(df, self.atr_lookback)
        
        # Dernière valeur - simple check: short-term ATR is low vs long-term
        atr_short_last = atr_short.iloc[-1]
        atr_long_last = atr_long.iloc[-1]
        
        # Compression: short-term volatility is significantly lower than long-term
        return atr_short_last < (self.atr_ratio * atr_long_last)
    
    def get_compression_metrics(self, df: pd.DataFrame) -> dict:
        """
        Retourne métriques détaillées de compression.
        
        Returns:
            Dict avec tous les métriques
        """
        if len(df) < self.atr_lookback:
            return {"error": "Insufficient data"}
        
        atr_short = self.calculate_atr(df, self.atr_period)
        atr_long = self.calculate_atr(df, self.atr_lookback)
        range_val = self.calculate_range(df, self.range_lookback)
        
        atr_short_last = atr_short.iloc[-1]
        atr_long_last = atr_long.iloc[-1]
        range_last = range_val.iloc[-1]
        
        atr_ratio_val = atr_short_last / atr_long_last if atr_long_last > 0 else 0
        range_ratio_val = range_last / atr_short_last if atr_short_last > 0 else 0
        
        return {
            "atr_14": atr_short_last,
            "atr_50": atr_long_last,
            "atr_ratio": atr_ratio_val,
            "atr_threshold": self.atr_ratio,
            "atr_compressed": atr_ratio_val < self.atr_ratio,
            "range_20": range_last,
            "range_ratio": range_ratio_val,
            "range_threshold": self.range_ratio,
            "range_compressed": range_ratio_val < self.range_ratio,
            "is_compression": (atr_ratio_val < self.atr_ratio) and (range_ratio_val < self.range_ratio),
        }
