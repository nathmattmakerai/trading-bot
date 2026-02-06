"""
Moteur de backtest futures.
"""

import pandas as pd
from typing import List, Dict, Optional
from enum import Enum


class TradeStatus(Enum):
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Trade:
    """Représente une trade."""
    
    def __init__(
        self,
        trade_id: int,
        timestamp: pd.Timestamp,
        instrument: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        size: int,
    ):
        self.trade_id = trade_id
        self.timestamp = timestamp
        self.instrument = instrument
        self.direction = direction
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.size = size
        self.status = TradeStatus.OPEN
        
        self.exit_timestamp = None
        self.exit_price = None
        self.exit_reason = None  # "tp", "sl", "session_end"
        self.pnl = None
        self.pnl_pct = None
    
    def close_trade(
        self,
        exit_price: float,
        exit_timestamp: pd.Timestamp,
        reason: str = "tp",
    ):
        """Ferme la trade."""
        self.exit_price = exit_price
        self.exit_timestamp = exit_timestamp
        self.exit_reason = reason
        self.status = TradeStatus.CLOSED
        
        # Calculer PnL
        if self.direction == "long":
            self.pnl = (exit_price - self.entry_price) * self.size
        else:  # short
            self.pnl = (self.entry_price - exit_price) * self.size
        
        self.pnl_pct = (self.pnl / (self.entry_price * self.size)) * 100


class BacktestEngine:
    """
    Moteur de backtest pour futures.
    """
    
    def __init__(self, starting_balance: float = 10000.0):
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.trades_list = []
        self.trade_counter = 0
        
        self.open_position: Optional[Trade] = None
        self.closed_trades: List[Trade] = []
        
        # Statistiques
        self.daily_pnl = 0
        self.trades_today = 0
        self.current_date = None
    
    def execute_trade(
        self,
        timestamp: pd.Timestamp,
        instrument: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        size: int,
    ) -> Trade:
        """
        Exécute une trade.
        
        Returns:
            Trade object
        """
        self.trade_counter += 1
        
        trade = Trade(
            trade_id=self.trade_counter,
            timestamp=timestamp,
            instrument=instrument,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            size=size,
        )
        
        self.open_position = trade
        self.trades_list.append(trade)
        self.trades_today += 1
        
        return trade
    
    def close_trade(
        self,
        exit_price: float,
        exit_timestamp: pd.Timestamp,
        reason: str = "tp",
    ) -> Optional[Trade]:
        """
        Ferme position ouverte.
        
        Returns:
            Closed trade object ou None
        """
        if not self.open_position:
            return None
        
        self.open_position.close_trade(exit_price, exit_timestamp, reason)
        
        # Update balance
        self.current_balance += self.open_position.pnl
        self.daily_pnl += self.open_position.pnl
        
        self.closed_trades.append(self.open_position)
        self.open_position = None
        
        return self.closed_trades[-1]
    
    def update_daily_metrics(self, new_date: pd.Timestamp):
        """Réinitialise métriques journalières."""
        if new_date.date() != self.current_date:
            self.current_date = new_date.date()
            self.daily_pnl = 0
            self.trades_today = 0
    
    def get_equity_curve(self) -> pd.DataFrame:
        """
        Retourne equity curve du backtest.
        
        Returns:
            DataFrame avec timestamps et equity values
        """
        equity_data = []
        running_balance = self.starting_balance
        
        for trade in self.closed_trades:
            running_balance += trade.pnl
            equity_data.append({
                "timestamp": trade.exit_timestamp,
                "equity": running_balance,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
            })
        
        if not equity_data:
            return pd.DataFrame()
        
        return pd.DataFrame(equity_data).set_index("timestamp")
    
    def get_statistics(self) -> dict:
        """
        Retourne statistiques complètes du backtest.
        
        Returns:
            Dict avec tous les metrics
        """
        if not self.closed_trades:
            return {"error": "No closed trades"}
        
        df_trades = pd.DataFrame([
            {
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
                "direction": t.direction,
                "exit_reason": t.exit_reason,
            }
            for t in self.closed_trades
        ])
        
        total_pnl = df_trades["pnl"].sum()
        total_return_pct = (total_pnl / self.starting_balance) * 100
        
        wins = df_trades[df_trades["pnl"] > 0]
        losses = df_trades[df_trades["pnl"] <= 0]
        
        win_rate = (len(wins) / len(df_trades)) * 100 if len(df_trades) > 0 else 0
        
        # Max drawdown
        equity_curve = self.get_equity_curve()
        if len(equity_curve) > 0:
            running_max = equity_curve["equity"].expanding().max()
            drawdown = (equity_curve["equity"] - running_max) / running_max
            max_drawdown = drawdown.min() * 100
        else:
            max_drawdown = 0
        
        return {
            "starting_balance": self.starting_balance,
            "final_balance": self.current_balance,
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "num_trades": len(self.closed_trades),
            "num_wins": len(wins),
            "num_losses": len(losses),
            "win_rate": win_rate,
            "avg_win": wins["pnl"].mean() if len(wins) > 0 else 0,
            "avg_loss": losses["pnl"].mean() if len(losses) > 0 else 0,
            "largest_win": wins["pnl"].max() if len(wins) > 0 else 0,
            "largest_loss": losses["pnl"].min() if len(losses) > 0 else 0,
            "max_drawdown_pct": max_drawdown,
        }
