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
        tick_value: float = 20.0,  # Par défaut NQ E-mini. Sera surchargé pour MNQ ($2)
    ) -> int:
        """
        Calcule nombre de contrats.
        """
        if account_balance <= 0 or stop_loss_distance <= 0:
            return 0
        
        # Risque autorisé en dollars (ex: $10,000 * 0.01 = $100)
        risk_allows_dollars = account_balance * self.risk_per_trade
        
        # Risque par contrat unique (ex: 20 points * $20/point = $400)
        risk_per_contract = stop_loss_distance * tick_value
        
        if risk_per_contract == 0:
            return 0
            
        # Nombre de contrats "théorique" selon le risque
        # Ex: $100 / $400 = 0.25 contrat
        raw_size = risk_allows_dollars / risk_per_contract
        
        contracts = int(raw_size)
        
        # Security: Don't force 1 contract if it represents > 10% of account risk 
        # This avoids "kamikaze" trades on small accounts.
        if contracts == 0:
            if risk_per_contract > (account_balance * 0.10):
                return 0
            return 1
            
        return contracts
    
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
