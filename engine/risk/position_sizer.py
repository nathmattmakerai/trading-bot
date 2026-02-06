"""
Position sizing: Risk management strict.

Règles:
- 0.75% risque par trade
- Max 2.5% drawdown daily
- Max 2 trades par jour
- Pas de pyramiding
- Contrats entiers uniquement
"""

import pandas as pd
from typing import Tuple, Optional


class PositionSizer:
    """
    Calcule taille position basée sur risk management strict.
    """
    
    def __init__(
        self,
        risk_per_trade: float = 0.0075,  # 0.75%
        max_daily_loss: float = 0.025,  # 2.5%
        max_trades_per_day: int = 2,
        contract_value: float = 1.0,  # 1 contrat futures
    ):
        """
        Args:
            risk_per_trade: Fraction de capital par trade (0.75%)
            max_daily_loss: Max loss daily (2.5%)
            max_trades_per_day: Max 2 trades/jour
            contract_value: Valeur nominale 1 contrat
        """
        self.risk_per_trade = risk_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_trades_per_day = max_trades_per_day
        self.contract_value = contract_value
    
    def calculate_position_size(
        self,
        account_balance: float,
        stop_loss_distance: float,
        tick_value: float = 20.0,  # Pour NQ/ES: 1 tick = $20
    ) -> int:
        """
        Calcule nombre de contrats.
        
        Formule:
        Risk_$ = account_balance × risk_per_trade
        Position_size = Risk_$ / (SL_distance × tick_value)
        -> Round down to whole contracts
        
        Args:
            account_balance: Solde compte
            stop_loss_distance: Distance SL en points (ex: 25 points)
            tick_value: Valeur 1 tick en dollars
        
        Returns:
            Nombre de contrats (entier positif)
        """
        if account_balance <= 0:
            return 0
        
        if stop_loss_distance <= 0:
            return 0
        
        # Risque en dollars
        risk_dollars = account_balance * self.risk_per_trade
        
        # SL distance en dollars
        sl_dollars = stop_loss_distance * tick_value
        
        # Taille position
        position_size = risk_dollars / sl_dollars
        
        # Arrondir vers le bas (whole contracts)
        contracts = int(position_size)
        
        # Min 1 contrat
        return max(1, contracts)
    
    def get_stop_loss(
        self,
        signal_direction: str,
        range_high: float,
        range_low: float,
    ) -> float:
        """
        Retourne niveau SL (autre côté du range).
        
        Args:
            signal_direction: 'long' ou 'short'
            range_high: Limite haute du range
            range_low: Limite basse du range
        
        Returns:
            Niveau SL
        """
        if signal_direction == "long":
            return range_low
        elif signal_direction == "short":
            return range_high
        else:
            return None
    
    def get_take_profit(
        self,
        signal_direction: str,
        entry_price: float,
        stop_loss: float,
        tp_ratio: float = 3.0,
    ) -> float:
        """
        Retourne niveau TP (3R fixe).
        
        Args:
            signal_direction: 'long' ou 'short'
            entry_price: Prix entrée
            stop_loss: Niveau SL
            tp_ratio: Ratio TP/SL (3.0 = 3R)
        
        Returns:
            Niveau TP
        """
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = sl_distance * tp_ratio
        
        if signal_direction == "long":
            return entry_price + tp_distance
        elif signal_direction == "short":
            return entry_price - tp_distance
        else:
            return None
    
    def can_take_trade(
        self,
        account_balance: float,
        daily_loss: float,
        trades_today: int,
        current_position: bool = False,
    ) -> Tuple[bool, str]:
        """
        Valide si on peut prendre trade selon risk rules.
        
        Args:
            account_balance: Solde courant
            daily_loss: Loss today en dollars
            trades_today: Nombre trades pris aujourd'hui
            current_position: Trade position ouverte?
        
        Returns:
            Tuple (can_trade, reason)
        """
        # Check max daily loss
        max_daily_loss_dollars = account_balance * self.max_daily_loss
        if daily_loss >= max_daily_loss_dollars:
            return False, f"Daily loss limit reached ({daily_loss:.2f})"
        
        # Check max trades per day
        if trades_today >= self.max_trades_per_day:
            return False, f"Max {self.max_trades_per_day} trades/day reached"
        
        # Check one-at-a-time rule
        if current_position:
            return False, "Position already open (one-trade-at-a-time)"
        
        return True, "OK - ready to trade"
    
    def get_risk_summary(
        self,
        account_balance: float,
        position_size: int,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        tick_value: float = 20.0,
    ) -> dict:
        """
        Résumé risque/reward du trade.
        
        Returns:
            Dict avec risk_dollars, reward_dollars, ratio, etc.
        """
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(entry_price - take_profit)
        
        risk_dollars = position_size * sl_distance * tick_value
        reward_dollars = position_size * tp_distance * tick_value
        
        ratio = reward_dollars / risk_dollars if risk_dollars > 0 else 0
        risk_pct = (risk_dollars / account_balance * 100) if account_balance > 0 else 0
        
        return {
            "position_size_contracts": position_size,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "sl_distance_points": sl_distance,
            "tp_distance_points": tp_distance,
            "risk_dollars": risk_dollars,
            "reward_dollars": reward_dollars,
            "risk_reward_ratio": ratio,
            "risk_pct_of_account": risk_pct,
        }
