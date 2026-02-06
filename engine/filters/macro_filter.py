"""
Filtre macro: VIX-based risk regime detection.
"""

import pandas as pd
from enum import Enum
from typing import Tuple


class RiskRegime(Enum):
    """Régimes de risque basés sur macro."""
    RISK_ON = "risk_on"  # Long autorisé
    RISK_OFF = "risk_off"  # Short only ou no trade
    NEUTRAL = "neutral"  # Sélectif


class MacroFilter:
    """
    Filtre macro obligatoire basé sur VIX et US10Y yield.
    
    Risk-on: VIX < 18, Yields stables ou en hausse -> Long autorisé
    Risk-off: VIX > 22 ou yields en chute violente -> Short only ou no-trade
    Neutral: Entre les deux -> Sélectif
    """
    
    def __init__(
        self,
        vix_risk_on_threshold: float = 18.0,
        vix_risk_off_threshold: float = 22.0,
        yield_change_threshold: float = 0.05,  # 5% decline = risk-off
    ):
        self.vix_risk_on = vix_risk_on_threshold
        self.vix_risk_off = vix_risk_off_threshold
        self.yield_change_threshold = yield_change_threshold
    
    def get_risk_regime(
        self,
        vix: float,
        us10y_yield: float,
        us10y_prev: float = None,
    ) -> RiskRegime:
        """
        Détermine régime de risque.
        
        Args:
            vix: VIX courant
            us10y_yield: US10Y courant
            us10y_prev: US10Y jour précédent (pour calculer changement)
        
        Returns:
            RiskRegime enum
        """
        # Vérifier VIX d'abord (signal dominant)
        if vix > self.vix_risk_off:
            return RiskRegime.RISK_OFF
        
        if vix < self.vix_risk_on:
            # VIX en zone risk-on
            # Vérifier yields
            if us10y_prev is not None:
                yield_change = (us10y_yield - us10y_prev) / us10y_prev
                if yield_change < -self.yield_change_threshold:
                    # Chute violente des yields = flight to safety
                    return RiskRegime.RISK_OFF
            
            return RiskRegime.RISK_ON
        
        # VIX entre 18 et 22
        return RiskRegime.NEUTRAL
    
    def is_long_allowed(self, regime: RiskRegime) -> bool:
        """Long autorisé en risk-on uniquement."""
        return regime == RiskRegime.RISK_ON
    
    def is_short_allowed(self, regime: RiskRegime) -> bool:
        """Short possible en risk-off et neutral."""
        return regime in [RiskRegime.RISK_OFF, RiskRegime.NEUTRAL]
    
    def should_trade(self, regime: RiskRegime, signal_direction: str) -> bool:
        """
        Détermine si un trade doit être exécuté selon filtre macro.
        
        Args:
            regime: RiskRegime courant
            signal_direction: 'long' ou 'short'
        
        Returns:
            True si trade compatible avec macro
        """
        if signal_direction == "long":
            return self.is_long_allowed(regime)
        elif signal_direction == "short":
            return self.is_short_allowed(regime)
        else:
            return False
    
    def filter_status(self, regime: RiskRegime) -> dict:
        """
        Retourne status détaillé du filtre macro.
        
        Returns:
            Dict avec long_allowed, short_allowed, regime
        """
        return {
            "regime": regime.value,
            "long_allowed": self.is_long_allowed(regime),
            "short_allowed": self.is_short_allowed(regime),
        }
