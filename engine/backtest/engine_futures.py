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
        is_virtual: bool = False,  # Nouveau flag
        metadata: dict = None,      # Contexte (VIX, ATR Ratio, etc.)
        multiplier: float = 1.0,    # Valeur d'un point (ex: 20 pour NQ)
        commission_per_contract: float = 0.0,
    ):
        self.trade_id = trade_id
        self.timestamp = timestamp
        self.instrument = instrument
        self.direction = direction
        self.entry_price = entry_price
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.size = size
        self.is_virtual = is_virtual
        self.metadata = metadata or {}
        self.multiplier = multiplier
        self.commission_total = (size * commission_per_contract) if not is_virtual else 0.0
        self.status = TradeStatus.OPEN
        
        self.exit_timestamp = None
        self.exit_price = None
        self.exit_reason = None  # "tp", "sl", "session_end"
        self.pnl = 0.0
        self.pnl_pct = 0.0
        self.virtual_pnl = 0.0
        self.pnl_pct_account = 0.0
    
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
        
        # Calculer PnL brut (Points * Taille * Multiplicateur)
        if self.direction == "long":
            raw_pnl = (exit_price - self.entry_price) * self.size * self.multiplier
        else:  # short
            raw_pnl = (self.entry_price - exit_price) * self.size * self.multiplier
        
        # Déduire commissions
        net_pnl = raw_pnl - self.commission_total
        
        # Si virtuel, le PnL réel est 0 mais on stocke le PnL théorique pour l'analyse
        self.pnl = net_pnl if not self.is_virtual else 0.0
        self.virtual_pnl = net_pnl  # PnL théorique (net)
        
        # PnL en % du nominal
        nominal_value = self.entry_price * self.size * self.multiplier
        self.pnl_pct = (self.virtual_pnl / nominal_value) * 100 if nominal_value > 0 else 0.0
        
        # Le PnL en % du compte sera calculé par l'engine qui connaît la balance
        self.pnl_pct_account = 0.0


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
        is_virtual: bool = False,
        metadata: dict = None,
        multiplier: float = 1.0,
        commission_per_contract: float = 0.0,
    ) -> Trade:
        """
        Exécute une trade.
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
            is_virtual=is_virtual,
            metadata=metadata,
            multiplier=multiplier,
            commission_per_contract=commission_per_contract,
        )
        
        self.open_position = trade
        self.trades_list.append(trade)
        # On compte les trades virtuels dans les stats globales ?
        # Pour l'instant oui, on filtrera plus tard
        if not is_virtual:
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
        
        # Calculer le PnL en % du compte (avant le trade pour la base)
        balance_before = self.current_balance
        
        # On ferme le trade d'abord pour calculer le virtual_pnl
        self.open_position.close_trade(exit_price, exit_timestamp, reason)
        
        if balance_before > 0:
            self.open_position.pnl_pct_account = (self.open_position.virtual_pnl / balance_before) * 100
        else:
            self.open_position.pnl_pct_account = 0.0
            
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
                "virtual_pnl": t.virtual_pnl,
                "pnl_pct": t.pnl_pct,
                "direction": t.direction,
                "exit_reason": t.exit_reason,
                "is_virtual": t.is_virtual,
                "is_learner": t.metadata.get("learner_skipped", False),
                "is_equity": t.metadata.get("equity_skipped", False),
                "is_filter": t.metadata.get("filter_skipped", False),
            }
            for t in self.closed_trades
        ])
        
        # Séparer réel et virtuel
        df_real = df_trades[~df_trades["is_virtual"]]
        df_learner = df_trades[df_trades["is_learner"]]
        df_equity = df_trades[df_trades["is_equity"]]
        df_filter = df_trades[df_trades["is_filter"]]
        
        num_virtual = len(df_trades) - len(df_real)
        
        # Stats Learner (Expérience)
        num_learner_wins = len(df_learner[df_learner["virtual_pnl"] > 0])
        num_learner_losses = len(df_learner[df_learner["virtual_pnl"] <= 0])
        
        # Stats Equity Guard (Protection Capital)
        num_equity_wins = len(df_equity[df_equity["virtual_pnl"] > 0])
        num_equity_losses = len(df_equity[df_equity["virtual_pnl"] <= 0])

        # Stats Filters (Macro/Session)
        num_filter_wins = len(df_filter[df_filter["virtual_pnl"] > 0])
        num_filter_losses = len(df_filter[df_filter["virtual_pnl"] <= 0])
        
        # Calculer stats sur trades REELS uniquement
        if len(df_real) == 0:
            total_pnl = 0
            total_return_pct = 0
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            largest_win = 0
            largest_loss = 0
        else:
            total_pnl = df_real["pnl"].sum()
            total_return_pct = (total_pnl / self.starting_balance) * 100
            
            wins = df_real[df_real["pnl"] > 0]
            losses = df_real[df_real["pnl"] <= 0]
            
            win_rate = (len(wins) / len(df_real)) * 100
            avg_win = wins["pnl"].mean() if len(wins) > 0 else 0
            avg_loss = losses["pnl"].mean() if len(losses) > 0 else 0
            largest_win = wins["pnl"].max() if len(wins) > 0 else 0
            largest_loss = losses["pnl"].min() if len(losses) > 0 else 0
        
        # Max drawdown
        equity_curve = self.get_equity_curve()
        if len(equity_curve) > 0:
            running_max = equity_curve["equity"].expanding().max()
            drawdown = (equity_curve["equity"] - running_max) / running_max
            max_drawdown = drawdown.min() * 100
        else:
            max_drawdown = 0
        
        # Diagnostic automatique
        diagnosis = "Performance normal."
        if num_equity_losses > 15:
            diagnosis = "🛡️ Equity Guard a sauvé votre compte : Trop de pertes consécutives détectées. Le marché était probablement trop haché."
        elif num_learner_losses > 15:
            diagnosis = "🧠 Learner Guard est efficace : Beaucoup de trades toxiques évités grâce à l'expérience passée."
        elif win_rate < 30 and len(df_real) > 0:
            diagnosis = "❌ Win Rate trop bas : Les breakouts sont peut-être trop tardifs ou le buffer ATR est trop petit."
        
        return {
            "starting_balance": self.starting_balance,
            "final_balance": self.current_balance,
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "num_trades": len(df_real),
            "num_virtual_trades": num_virtual,
            "num_learner_wins": num_learner_wins,
            "num_learner_losses": num_learner_losses,
            "num_equity_wins": num_equity_wins,
            "num_equity_losses": num_equity_losses,
            "num_filter_wins": num_filter_wins,
            "num_filter_losses": num_filter_losses,
            "num_wins": len(df_real[df_real["pnl"] > 0]),
            "num_losses": len(df_real[df_real["pnl"] <= 0]),
            "win_rate": win_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "max_drawdown_pct": max_drawdown,
            "diagnosis": diagnosis,
            "num_breakeven": len(df_real[df_real["exit_reason"] == "be"]) if "exit_reason" in df_real.columns else 0
        }
