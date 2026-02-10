"""
Enhanced Backtest Runner for FTMO Trading Bot
Provides comprehensive backtesting with statistics, analysis, and optimization.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass

from main import TradingBot
from engine.backtest.engine_futures import BacktestEngine


@dataclass
class BacktestResult:
    """Container for backtest results."""
    instrument: str
    start_date: str
    end_date: str
    starting_balance: float
    final_balance: float
    total_pnl: float
    total_return_pct: float
    
    # Trade statistics
    num_trades: int
    num_wins: int
    num_losses: int
    num_breakeven: int
    win_rate: float
    loss_rate: float
    
    # P&L statistics
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    total_wins: float
    total_losses: float
    profit_factor: float
    
    # Risk metrics
    max_drawdown_pct: float
    max_drawdown_amount: float
    drawdown_duration: int
    
    # Performance metrics
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    recovery_factor: float
    
    # Daily/Monthly breakdown
    daily_pnl_list: List[float]
    monthly_pnl_dict: Dict[str, float]
    
    # Trade list for detailed analysis
    trades: List[dict]
    equity_curve: List[float]
    num_virtual_trades: int = 0
    num_learner_wins: int = 0
    num_learner_losses: int = 0
    num_equity_wins: int = 0
    num_equity_losses: int = 0
    num_filter_wins: int = 0
    num_filter_losses: int = 0
    diagnosis: str = "No diagnosis"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "instrument": self.instrument,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "starting_balance": self.starting_balance,
            "final_balance": self.final_balance,
            "total_pnl": self.total_pnl,
            "total_return_pct": self.total_return_pct,
            "num_trades": self.num_trades,
            "num_wins": self.num_wins,
            "num_losses": self.num_losses,
            "num_breakeven": self.num_breakeven,
            "win_rate": self.win_rate,
            "loss_rate": self.loss_rate,
            "avg_win": self.avg_win,
            "avg_loss": self.avg_loss,
            "largest_win": self.largest_win,
            "largest_loss": self.largest_loss,
            "total_wins": self.total_wins,
            "total_losses": self.total_losses,
            "profit_factor": self.profit_factor,
            "max_drawdown_pct": self.max_drawdown_pct,
            "max_drawdown_amount": self.max_drawdown_amount,
            "drawdown_duration": self.drawdown_duration,
            "sharpe_ratio": self.sharpe_ratio,
            "sortino_ratio": self.sortino_ratio,
            "calmar_ratio": self.calmar_ratio,
            "recovery_factor": self.recovery_factor,
            "monthly_pnl": self.monthly_pnl_dict,
            "equity_curve": self.equity_curve,
        }


class BacktestAnalyzer:
    """Analyzes backtest results and computes advanced metrics."""
    
    def __init__(self, bot: TradingBot, risk_free_rate: float = 0.04):
        """
        Initialize analyzer.
        
        Args:
            bot: TradingBot instance after backtest
            risk_free_rate: Annual risk-free rate (default 4%)
        """
        self.bot = bot
        self.engine = bot.backtest_engine
        self.risk_free_rate = risk_free_rate
    
    def compute_all_metrics(self) -> BacktestResult:
        """Compute all backtest metrics."""
        trades = self._extract_trades()
        equity_curve = self._get_equity_curve()
        
        # Filter real trades
        real_trades = [t for t in trades if not t.get("is_virtual", False)]
        num_virtual = len(trades) - len(real_trades)
        
        # Basic metrics (on REAL trades only)
        basic = self._compute_basic_metrics(real_trades)
        
        # Risk metrics (equity curve already flat for virtual trades)
        risk = self._compute_risk_metrics(equity_curve)
        
        # Performance metrics
        perf = self._compute_performance_metrics(equity_curve)
        
        # Daily/Monthly breakdown (REAL trades only)
        daily_pnl = self._compute_daily_pnl(real_trades)
        monthly_pnl = self._compute_monthly_pnl(real_trades)
        
        res = BacktestResult(
            instrument=self.bot.rules.get("instrument", "UNKNOWN"),
            start_date="",
            end_date="",
            starting_balance=self.engine.starting_balance,
            final_balance=self.engine.current_balance,
            total_pnl=basic["total_pnl"],
            total_return_pct=basic["total_return_pct"],
            
            # Trade stats from basic metrics
            num_trades=basic["num_trades"],
            num_wins=basic["num_wins"],
            num_losses=basic["num_losses"],
            num_breakeven=basic["num_breakeven"],
            win_rate=basic["win_rate"],
            loss_rate=basic["loss_rate"],
            num_virtual_trades=num_virtual,
            num_learner_wins=0,
            num_learner_losses=0,
            num_equity_wins=0,
            num_equity_losses=0,
            num_filter_wins=0,
            num_filter_losses=0,
            diagnosis="",
            avg_win=basic["avg_win"],
            avg_loss=basic["avg_loss"],
            largest_win=basic["largest_win"],
            largest_loss=basic["largest_loss"],
            total_wins=basic["total_wins"],
            total_losses=basic["total_losses"],
            profit_factor=basic["profit_factor"],
            max_drawdown_pct=risk["max_drawdown_pct"],
            max_drawdown_amount=risk["max_drawdown_amount"],
            drawdown_duration=risk["drawdown_duration"],
            sharpe_ratio=perf["sharpe_ratio"],
            sortino_ratio=perf["sortino_ratio"],
            calmar_ratio=perf["calmar_ratio"],
            recovery_factor=perf["recovery_factor"],
            daily_pnl_list=daily_pnl,
            monthly_pnl_dict=monthly_pnl,
            trades=trades,
            equity_curve=equity_curve,
        )
        
        # Populate from engine's detailed stats
        detailed_stats = self.engine.get_statistics()
        res.num_learner_wins = detailed_stats.get("num_learner_wins", 0)
        res.num_learner_losses = detailed_stats.get("num_learner_losses", 0)
        res.num_equity_wins = detailed_stats.get("num_equity_wins", 0)
        res.num_equity_losses = detailed_stats.get("num_equity_losses", 0)
        res.num_filter_wins = detailed_stats.get("num_filter_wins", 0)
        res.num_filter_losses = detailed_stats.get("num_filter_losses", 0)
        res.diagnosis = detailed_stats.get("diagnosis", "")
        
        return res
    
    def _extract_trades(self) -> List[dict]:
        """Extract trade details from closed trades."""
        trades = []
        for trade in self.engine.closed_trades:
            trades.append({
                "trade_id": trade.trade_id,
                "entry_date": str(trade.timestamp),
                "exit_date": str(trade.exit_timestamp),
                "instrument": trade.instrument,
                "direction": trade.direction,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price,
                "stop_loss": trade.stop_loss,
                "take_profit": trade.take_profit,
                "size": trade.size,
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "exit_reason": trade.exit_reason,
                "is_virtual": trade.is_virtual,
            })
        return trades
    
    def _get_equity_curve(self) -> List[float]:
        """Get equity curve as list."""
        equity_df = self.engine.get_equity_curve()
        if len(equity_df) == 0:
            return [self.engine.starting_balance]
        return equity_df["equity"].tolist()
    
    def _compute_basic_metrics(self, trades: List[dict]) -> dict:
        """Compute basic trade metrics."""
        if not trades:
            return {
                "total_pnl": 0,
                "total_return_pct": 0,
                "num_trades": 0,
                "num_wins": 0,
                "num_losses": 0,
                "num_breakeven": 0,
                "win_rate": 0,
                "loss_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "largest_win": 0,
                "largest_loss": 0,
                "total_wins": 0,
                "total_losses": 0,
                "profit_factor": 0,
            }
        
        pnls = [t["pnl"] for t in trades]
        total_pnl = sum(pnls)
        total_return_pct = (total_pnl / self.engine.starting_balance) * 100
        
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]
        breakevens = [p for p in pnls if p == 0]
        
        win_rate = (len(wins) / len(trades)) * 100 if trades else 0
        loss_rate = (len(losses) / len(trades)) * 100 if trades else 0
        
        avg_win = np.mean(wins) if wins else 0
        avg_loss = np.mean(losses) if losses else 0
        largest_win = max(wins) if wins else 0
        largest_loss = min(losses) if losses else 0
        total_wins = sum(wins) if wins else 0
        total_losses = sum(losses) if losses else 0
        profit_factor = abs(total_wins / total_losses) if total_losses != 0 else 0
        
        return {
            "total_pnl": total_pnl,
            "total_return_pct": total_return_pct,
            "num_trades": len(trades),
            "num_wins": len(wins),
            "num_losses": len(losses),
            "num_breakeven": len(breakevens),
            "win_rate": win_rate,
            "loss_rate": loss_rate,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "total_wins": total_wins,
            "total_losses": total_losses,
            "profit_factor": profit_factor,
        }
    
    def _compute_risk_metrics(self, equity_curve: List[float]) -> dict:
        """Compute risk metrics (drawdown, etc)."""
        if not equity_curve or len(equity_curve) < 2:
            return {
                "max_drawdown_pct": 0,
                "max_drawdown_amount": 0,
                "drawdown_duration": 0,
            }
        
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdowns = (equity_series - running_max) / running_max
        
        max_drawdown_pct = drawdowns.min() * 100
        max_drawdown_amount = (drawdowns * running_max).min()
        
        # Drawdown duration (longest consecutive negative returns)
        drawdown_duration = 0
        current_dd_duration = 0
        for dd in drawdowns:
            if dd < 0:
                current_dd_duration += 1
                drawdown_duration = max(drawdown_duration, current_dd_duration)
            else:
                current_dd_duration = 0
        
        return {
            "max_drawdown_pct": max_drawdown_pct,
            "max_drawdown_amount": max_drawdown_amount,
            "drawdown_duration": drawdown_duration,
        }
    
    def _compute_performance_metrics(self, equity_curve: List[float]) -> dict:
        """Compute advanced performance metrics (Sharpe, Sortino, etc)."""
        if not equity_curve or len(equity_curve) < 2:
            return {
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "calmar_ratio": 0,
                "recovery_factor": 0,
            }
        
        # Calculate returns
        equity_series = pd.Series(equity_curve)
        returns = equity_series.pct_change().dropna()
        
        if len(returns) == 0:
            return {
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "calmar_ratio": 0,
                "recovery_factor": 0,
            }
        
        # Sharpe Ratio (252 trading days per year)
        excess_returns = returns - (self.risk_free_rate / 252)
        sharpe = excess_returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else 0
        
        # Sortino Ratio (only penalize downside volatility)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino = excess_returns.mean() / downside_std * np.sqrt(252) if downside_std != 0 else 0
        
        # Calmar Ratio (return / max drawdown)
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        max_dd = abs(self._compute_risk_metrics(equity_curve)["max_drawdown_pct"] / 100)
        calmar = total_return / max_dd if max_dd != 0 else 0
        
        # Recovery Factor (total profit / max drawdown)
        total_pnl = equity_curve[-1] - equity_curve[0]
        max_dd_amount = abs(self._compute_risk_metrics(equity_curve)["max_drawdown_amount"])
        recovery = total_pnl / max_dd_amount if max_dd_amount != 0 else 0
        
        return {
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "calmar_ratio": calmar,
            "recovery_factor": recovery,
        }
    
    def _compute_daily_pnl(self, trades: List[dict]) -> List[float]:
        """Compute daily P&L."""
        if not trades:
            return []
        
        daily_pnl = {}
        for trade in trades:
            exit_date = str(trade["exit_date"]).split(" ")[0]
            daily_pnl[exit_date] = daily_pnl.get(exit_date, 0) + trade["pnl"]
        
        return list(daily_pnl.values())
    
    def _compute_monthly_pnl(self, trades: List[dict]) -> Dict[str, float]:
        """Compute monthly P&L."""
        if not trades:
            return {}
        
        monthly_pnl = {}
        for trade in trades:
            exit_date = str(trade["exit_date"]).split(" ")[0]
            year_month = exit_date[:7]  # YYYY-MM
            monthly_pnl[year_month] = monthly_pnl.get(year_month, 0) + trade["pnl"]
        
        return monthly_pnl


class BacktestRunner:
    """Main backtest runner with enhanced functionality."""
    
    def __init__(self, starting_balance: float = 10000.0, custom_risk_config: dict = None, custom_contract_config: dict = None):
        """
        Initialize runner.
        
        Args:
            starting_balance: Capital de départ
            custom_risk_config: Configuration de risque personnalisée
            custom_contract_config: Configuration contrat (e.g. tick_value)
        """
        self.starting_balance = starting_balance
        self.custom_risk_config = custom_risk_config
        self.custom_contract_config = custom_contract_config
    
    def run_backtest(
        self,
        instrument: str,
        start_date: str,
        end_date: str,
    ) -> BacktestResult:
        """
        Run complete backtest.
        
        Args:
            instrument: 'NQ', 'ES', or 'YM'
            start_date: 'YYYY-MM-DD'
            end_date: 'YYYY-MM-DD'
        
        Returns:
            BacktestResult with all metrics
        """
        print(f"[Backtest] Running {instrument} from {start_date} to {end_date}")
        
        # Initialize bot with custom configs
        bot = TradingBot(
            starting_balance=self.starting_balance,
            custom_risk_config=self.custom_risk_config,
            custom_contract_config=self.custom_contract_config
        )
        
        # Run backtest
        bot.backtest(instrument, start_date, end_date)
        
        # Analyze results
        analyzer = BacktestAnalyzer(bot)
        result = analyzer.compute_all_metrics()
        
        # Set dates
        result.instrument = instrument
        result.start_date = start_date
        result.end_date = end_date
        
        return result
    
    def run_parameter_optimization(
        self,
        instrument: str,
        start_date: str,
        end_date: str,
        parameter_ranges: Dict[str, List],
    ) -> List[Tuple[Dict, BacktestResult]]:
        """
        Run multiple backtests with different parameters.
        
        Args:
            instrument: 'NQ', 'ES', or 'YM'
            start_date: 'YYYY-MM-DD'
            end_date: 'YYYY-MM-DD'
            parameter_ranges: Dict with parameter names and ranges
        
        Returns:
            List of (parameters, result) tuples sorted by Sharpe ratio
        """
        print(f"[Optimization] Testing {instrument}...")
        
        results = []
        
        # This is a placeholder - would need to integrate with config system
        # For now, just run single backtest
        result = self.run_backtest(instrument, start_date, end_date)
        results.append(({}, result))
        
        return results
    
    def run_walk_forward(
        self,
        instrument: str,
        start_date: str,
        end_date: str,
        window_size_months: int = 3,
    ) -> List[BacktestResult]:
        """
        Run walk-forward analysis.
        
        Args:
            instrument: 'NQ', 'ES', or 'YM'
            start_date: 'YYYY-MM-DD'
            end_date: 'YYYY-MM-DD'
            window_size_months: Training window size in months
        
        Returns:
            List of BacktestResult for each window
        """
        print(f"[Walk-Forward] Testing {instrument} with {window_size_months}m window...")
        
        results = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date < end_dt:
            window_end = current_date + timedelta(days=30 * window_size_months)
            if window_end > end_dt:
                window_end = end_dt
            
            print(f"  Testing window: {current_date.date()} to {window_end.date()}")
            
            result = self.run_backtest(
                instrument,
                current_date.strftime("%Y-%m-%d"),
                window_end.strftime("%Y-%m-%d"),
            )
            results.append(result)
            
            # Move forward by window size
            current_date = window_end
        
        return results


if __name__ == "__main__":
    # Example: Run single backtest
    runner = BacktestRunner(starting_balance=10000.0)
    result = runner.run_backtest("NQ", "2024-01-01", "2024-12-31")
    
    print("\n" + "=" * 80)
    print("BACKTEST RESULTS")
    print("=" * 80)
    print(f"Instrument:      {result.instrument}")
    print(f"Period:          {result.start_date} to {result.end_date}")
    print()
    print(f"Starting Balance: ${result.starting_balance:,.2f}")
    print(f"Final Balance:    ${result.final_balance:,.2f}")
    print(f"Total P&L:        ${result.total_pnl:,.2f}")
    print(f"Return:           {result.total_return_pct:.2f}%")
    print()
    print(f"Total Trades:     {result.num_trades}")
    print(f"Win Rate:         {result.win_rate:.1f}%")
    print(f"Profit Factor:    {result.profit_factor:.2f}")
    print()
    print(f"Max Drawdown:     {result.max_drawdown_pct:.2f}%")
    print(f"Sharpe Ratio:     {result.sharpe_ratio:.2f}")
    print(f"Sortino Ratio:    {result.sortino_ratio:.2f}")
    print("=" * 80)
