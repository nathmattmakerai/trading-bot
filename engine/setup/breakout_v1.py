"""
Setup v1: Breakout bidirectionnel de compression.
"""

import pandas as pd
from typing import Tuple, Optional


class BreakoutSetupV1:
    """
    Setup unique pour v1: Breakout bidirectionnel de compression.
    
    Logique:
    1. Détecter compression (compression_detector)
    2. Attendre breakout des bornes du range
    3. Long si close > max(range[-20:])
    4. Short si close < min(range[-20:])
    5. Pas de fakeout intra-bar (confirmation close)
    """
    
    def __init__(self, range_lookback: int = 20):
        """
        Args:
            range_lookback: Nombre de bougies pour calculer range
        """
        self.range_lookback = range_lookback
    
    def calculate_range_bounds(self, df: pd.DataFrame) -> Tuple[float, float]:
        """
        Calcule bornes du range.
        
        Args:
            df: DataFrame avec colonnes [high, low]
        
        Returns:
            Tuple (range_high, range_low)
        """
        if len(df) < self.range_lookback:
            return None, None
        
        recent = df.tail(self.range_lookback)
        range_high = recent["high"].max()
        range_low = recent["low"].min()
        
        return range_high, range_low
    
    def detect_long_breakout(self, df: pd.DataFrame) -> bool:
        """
        Détecte long breakout: close > max(range[-20:]).
        
        Args:
            df: DataFrame avec dernière bougie à vérifier
        
        Returns:
            True si long breakout confirmé
        """
        range_high, _ = self.calculate_range_bounds(df)
        
        if range_high is None:
            return False
        
        close = df["close"].iloc[-1]
        return close > range_high
    
    def detect_short_breakout(self, df: pd.DataFrame) -> bool:
        """
        Détecte short breakout: close < min(range[-20:]).
        
        Args:
            df: DataFrame avec dernière bougie à vérifier
        
        Returns:
            True si short breakout confirmé
        """
        _, range_low = self.calculate_range_bounds(df)
        
        if range_low is None:
            return False
        
        close = df["close"].iloc[-1]
        return close < range_low
    
    def get_breakout_signal(self, df: pd.DataFrame) -> Optional[str]:
        """
        Retourne signal de breakout (long/short/None).
        
        Args:
            df: DataFrame avec dernière bougie
        
        Returns:
            'long', 'short', ou None
        """
        long_signal = self.detect_long_breakout(df)
        short_signal = self.detect_short_breakout(df)
        
        if long_signal:
            return "long"
        elif short_signal:
            return "short"
        else:
            return None
    
    def get_setup_levels(self, df: pd.DataFrame) -> dict:
        """
        Retourne niveaux clés du setup.
        
        Returns:
            Dict avec range_high, range_low, current_close
        """
        range_high, range_low = self.calculate_range_bounds(df)
        current_close = df["close"].iloc[-1] if len(df) > 0 else None
        
        return {
            "range_high": range_high,
            "range_low": range_low,
            "current_close": current_close,
            "range_width": (range_high - range_low) if range_high else None,
        }
    
    def validate_setup(
        self,
        df: pd.DataFrame,
        is_compression: bool,
    ) -> Tuple[bool, str]:
        """
        Valide si setup complet: compression + breakout.
        
        Args:
            df: DataFrame
            is_compression: Résultat CompressionDetector
        
        Returns:
            Tuple (setup_valid, reason)
        """
        if not is_compression:
            return False, "No compression detected"
        
        signal = self.get_breakout_signal(df)
        
        if signal:
            return True, f"Valid {signal} setup"
        else:
            return False, "No breakout yet"
