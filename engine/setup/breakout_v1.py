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
        Calcule bornes du range sur les N bougies précédentes (excluant la dernière).
        
        Le range exclut la bougie actuelle pour permettre de détecter si 
        le close actuel brise le range précédent.
        
        Args:
            df: DataFrame avec colonnes [high, low]
        
        Returns:
            Tuple (range_high, range_low)
        """
        # On a besoin d'au moins range_lookback + 1 bougies 
        # (les 20 précédentes + la bougie actuelle)
        if len(df) < self.range_lookback + 1:
            return None, None
        
        # Exclure la dernière bougie pour le calcul du range
        # Prendre les range_lookback bougies avant la dernière
        recent = df.iloc[-(self.range_lookback + 1):-1]
        range_high = recent["high"].max()
        range_low = recent["low"].min()
        
        return range_high, range_low
    
    def detect_long_breakout(self, df: pd.DataFrame) -> bool:
        """
        Détecte long breakout avec buffer ATR pour éviter bruit.
        """
        range_high, _ = self.calculate_range_bounds(df)
        if range_high is None: return False
        
        # Calcul ATR pour buffer
        from engine.structure.compression_detector import CompressionDetector
        cd = CompressionDetector()
        atr = cd.calculate_atr(df, 14).iloc[-1]
        buffer = atr * 0.10 # 10% ATR buffer (Plus robuste)
        
        close = df["close"].iloc[-1]
        return close > (range_high + buffer)
    
    def detect_short_breakout(self, df: pd.DataFrame) -> bool:
        """
        Détecte short breakout avec buffer ATR.
        """
        _, range_low = self.calculate_range_bounds(df)
        if range_low is None: return False
        
        from engine.structure.compression_detector import CompressionDetector
        cd = CompressionDetector()
        atr = cd.calculate_atr(df, 14).iloc[-1]
        buffer = atr * 0.05 # 5% ATR buffer
        
        close = df["close"].iloc[-1]
        return close < (range_low - buffer)
    
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
