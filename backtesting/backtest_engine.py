"""
Realistic Backtesting Engine for Trading Bot

This module implements realistic backtesting with transaction costs, slippage,
and execution quality to ensure backtest results are representative of real trading conditions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeResult:
    """Represents the result of a single trade"""
    symbol: str
    entry_price: float
    exit_price: float
    quantity: float
    side: str  # 'long' or 'short'
    entry_time: datetime
    exit_time: datetime
    profit_loss: float
    transaction_cost: float
    slippage_cost: float
    total_cost: float

@dataclass
class BacktestMetrics:
    """Container for backtest performance metrics"""
    total_return: float
    annualized_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    avg_win: float
    avg_loss: float
    total_trades: int
    total_transaction_costs: float
    total_slippage_costs: float

class ExecutionQuality(Enum):
    """Enum for different execution quality levels"""
    PERFECT = "perfect"      # No slippage, no transaction costs
    GOOD = "good"            # Reasonable slippage and costs
    FAIR = "fair"            # Moderate slippage and costs
    POOR = "poor"            # High slippage and costs

class BacktestEngine:
    """
    Realistic backtesting engine that incorporates transaction costs,
    slippage, and execution quality to provide representative results.
    """

    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize the backtest engine

        Args:
            initial_capital (float): Starting capital for backtesting
        """
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades: List[TradeResult] = []
        self.portfolio_history: List[Dict] = []
        self.execution_quality = ExecutionQuality.GOOD
        self.transaction_cost_rate = 0.001  # 0.1% per trade
        self.slippage_rate = 0.0005  # 0.05% slippage

    def set_execution_quality(self, quality: ExecutionQuality) -> None:
        """
        Set the execution quality level for backtesting

        Args:
            quality (ExecutionQuality): Quality level to use
        """
        self.execution_quality = quality

        # Adjust rates based on quality level
        if quality == ExecutionQuality.PERFECT:
            self.transaction_cost_rate = 0.0
            self.slippage_rate = 0.0
        elif quality == ExecutionQuality.GOOD:
            self.transaction_cost_rate = 0.001  # 0.1%
            self.slippage_rate = 0.0005  # 0.05%
        elif quality == ExecutionQuality.FAIR:
            self.transaction_cost_rate = 0.002  # 0.2%
            self.slippage_rate = 0.001  # 0.1%
        elif quality == ExecutionQuality.POOR:
            self.transaction_cost_rate = 0.005  # 0.5%
            self.slippage_rate = 0.003  # 0.3%

        logger.info(f"Execution quality set to {quality.value}")

    def calculate_transaction_costs(self, price: float, quantity: float) -> float:
        """
        Calculate transaction costs for a trade

        Args:
            price (float): Price of the trade
            quantity (float): Quantity traded

        Returns:
            float: Transaction cost amount
        """
        cost = price * quantity * self.transaction_cost_rate
        return cost

    def calculate_slippage(self, price: float, quantity: float) -> float:
        """
        Calculate slippage costs for a trade

        Args:
            price (float): Price of the trade
            quantity (float): Quantity traded

        Returns:
            float: Slippage cost amount
        """
        # Slippage is calculated as a percentage of the trade value
        slippage = price * quantity * self.slippage_rate
        return slippage

    def simulate_trade_execution(self,
                               symbol: str,
                               entry_price: float,
                               exit_price: float,
                               quantity: float,
                               side: str,
                               entry_time: datetime,
                               exit_time: datetime) -> TradeResult:
        """
        Simulate realistic trade execution with costs and slippage

        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price
            exit_price (float): Exit price
            quantity (float): Quantity traded
            side (str): 'long' or 'short'
            entry_time (datetime): Entry timestamp
            exit_time (datetime): Exit timestamp

        Returns:
            TradeResult: Result of the simulated trade
        """
        # Calculate gross profit/loss
        if side == 'long':
            gross_profit = (exit_price - entry_price) * quantity
        else:  # short position
            gross_profit = (entry_price - exit_price) * quantity

        # Calculate costs
        entry_cost = self.calculate_transaction_costs(entry_price, quantity)
        exit_cost = self.calculate_transaction_costs(exit_price, quantity)
        entry_slippage = self.calculate_slippage(entry_price, quantity)
        exit_slippage = self.calculate_slippage(exit_price, quantity)

        total_transaction_cost = entry_cost + exit_cost
        total_slippage_cost = entry_slippage + exit_slippage
        total_cost = total_transaction_cost + total_slippage_cost

        # Calculate net profit/loss
        net_profit_loss = gross_profit - total_cost

        # Create trade result
        trade_result = TradeResult(
            symbol=symbol,
            entry_price=entry_price,
            exit_price=exit_price,
            quantity=quantity,
            side=side,
            entry_time=entry_time,
            exit_time=exit_time,
            profit_loss=net_profit_loss,
            transaction_cost=total_transaction_cost,
            slippage_cost=total_slippage_cost,
            total_cost=total_cost
        )

        # Update portfolio capital
        self.current_capital += net_profit_loss

        # Record trade
        self.trades.append(trade_result)

        return trade_result

    def run_backtest(self,
                    strategy_function,
                    data: pd.DataFrame,
                    symbol: str = "NQ",
                    position_size: float = 1.0) -> BacktestMetrics:
        """
        Run a backtest using the provided strategy

        Args:
            strategy_function: Function that takes data and returns trade signals
            data (pd.DataFrame): Historical price data
            symbol (str): Trading symbol
            position_size (float): Size of each position

        Returns:
            BacktestMetrics: Performance metrics from the backtest
        """
        logger.info(f"Starting backtest with {len(data)} data points")

        # Reset state
        self.current_capital = self.initial_capital
        self.trades = []
        self.portfolio_history = []

        # Initialize portfolio tracking
        self.portfolio_history.append({
            'timestamp': data.index[0],
            'capital': self.current_capital,
            'position': 0
        })

        # Track positions
        position = 0
        entry_price = 0.0
        entry_time = None

        # Process each data point
        for i in range(len(data) - 1):  # Leave one point for exit
            current_data = data.iloc[i]
            next_data = data.iloc[i + 1]

            # Get signals from strategy
            signal = strategy_function(current_data)

            # Handle position management
            if signal == 'BUY' and position == 0:
                # Enter long position
                entry_price = current_data['close']
                entry_time = current_data.name
                position = position_size

            elif signal == 'SELL' and position > 0:
                # Exit long position
                exit_price = next_data['open']  # Use open price of next bar for execution
                exit_time = next_data.name

                trade_result = self.simulate_trade_execution(
                    symbol=symbol,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=position,
                    side='long',
                    entry_time=entry_time,
                    exit_time=exit_time
                )

                # Update position tracking
                position = 0

            elif signal == 'SELL_SHORT' and position == 0:
                # Enter short position
                entry_price = current_data['close']
                entry_time = current_data.name
                position = -position_size  # Negative for short positions

            elif signal == 'BUY_TO_COVER' and position < 0:
                # Exit short position
                exit_price = next_data['open']  # Use open price of next bar for execution
                exit_time = next_data.name

                trade_result = self.simulate_trade_execution(
                    symbol=symbol,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    quantity=-position,  # Convert back to positive for calculation
                    side='short',
                    entry_time=entry_time,
                    exit_time=exit_time
                )

                # Update position tracking
                position = 0

            # Update portfolio history for tracking
            if i % 10 == 0:  # Record every 10th point to reduce memory usage
                self.portfolio_history.append({
                    'timestamp': current_data.name,
                    'capital': self.current_capital,
                    'position': position
                })

        # Calculate metrics
        metrics = self._calculate_metrics()
        logger.info(f"Backtest completed. Final capital: ${self.current_capital:.2f}")

        return metrics

    def _calculate_metrics(self) -> BacktestMetrics:
        """
        Calculate performance metrics from backtest results

        Returns:
            BacktestMetrics: Performance metrics
        """
        if not self.trades:
            return BacktestMetrics(
                total_return=0.0,
                annualized_return=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                win_rate=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                total_trades=0,
                total_transaction_costs=0.0,
                total_slippage_costs=0.0
            )

        # Calculate total return
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital

        # Calculate transaction and slippage costs
        total_transaction_costs = sum(trade.transaction_cost for trade in self.trades)
        total_slippage_costs = sum(trade.slippage_cost for trade in self.trades)

        # Calculate win rate and average wins/losses
        profits = [trade.profit_loss for trade in self.trades if trade.profit_loss > 0]
        losses = [trade.profit_loss for trade in self.trades if trade.profit_loss < 0]

        win_rate = len(profits) / len(self.trades) if self.trades else 0.0
        avg_win = sum(profits) / len(profits) if profits else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0

        # Calculate max drawdown (simplified)
        portfolio_values = [record['capital'] for record in self.portfolio_history]
        max_drawdown = 0.0
        if portfolio_values:
            peak = portfolio_values[0]
            for value in portfolio_values:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)

        # Calculate Sharpe ratio (simplified - assuming 0 risk-free rate)
        returns = []
        for i in range(1, len(self.portfolio_history)):
            prev_capital = self.portfolio_history[i-1]['capital']
            curr_capital = self.portfolio_history[i]['capital']
            if prev_capital > 0:
                return_val = (curr_capital - prev_capital) / prev_capital
                returns.append(return_val)

        if len(returns) > 1:
            std_dev = np.std(returns)
            annualized_return = total_return * 252 / len(self.portfolio_history) if self.portfolio_history else 0.0
            sharpe_ratio = annualized_return / std_dev if std_dev > 0 else 0.0
        else:
            sharpe_ratio = 0.0
            annualized_return = total_return

        return BacktestMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_trades=len(self.trades),
            total_transaction_costs=total_transaction_costs,
            total_slippage_costs=total_slippage_costs
        )

    def get_trade_history(self) -> List[TradeResult]:
        """
        Get the complete trade history

        Returns:
            List[TradeResult]: List of all trades executed
        """
        return self.trades

    def get_portfolio_history(self) -> List[Dict]:
        """
        Get the portfolio value history

        Returns:
            List[Dict]: List of portfolio values over time
        """
        return self.portfolio_history

    def print_summary(self) -> None:
        """
        Print a summary of backtest results
        """
        if not self.trades:
            print("No trades executed in backtest")
            return

        metrics = self._calculate_metrics()

        print("\n=== BACKTEST SUMMARY ===")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${self.current_capital:,.2f}")
        print(f"Total Return: {metrics.total_return*100:.2f}%")
        print(f"Annualized Return: {metrics.annualized_return*100:.2f}%")
        print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"Max Drawdown: {metrics.max_drawdown*100:.2f}%")
        print(f"Win Rate: {metrics.win_rate*100:.2f}%")
        print(f"Total Trades: {metrics.total_trades}")
        print(f"Total Transaction Costs: ${metrics.total_transaction_costs:,.2f}")
        print(f"Total Slippage Costs: ${metrics.total_slippage_costs:,.2f}")

# Example strategy function for testing
def example_strategy(data):
    """
    Simple example strategy that buys when price crosses above moving average
    and sells when it crosses below.

    Args:
        data (pd.Series): Price data

    Returns:
        str: 'BUY', 'SELL', or 'HOLD'
    """
    # Simple moving average crossover strategy
    if len(data) < 20:
        return 'HOLD'

    ma_5 = data['close'].rolling(5).mean().iloc[-1]
    ma_20 = data['close'].rolling(20).mean().iloc[-1]

    if ma_5 > ma_20:
        return 'BUY'
    elif ma_5 < ma_20:
        return 'SELL'
    else:
        return 'HOLD'

# Example usage
if __name__ == "__main__":
    # Create sample data for testing
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    prices = 18000 + np.cumsum(np.random.randn(100) * 50)

    sample_data = pd.DataFrame({
        'open': prices,
        'high': prices + np.abs(np.random.randn(100) * 30),
        'low': prices - np.abs(np.random.randn(100) * 30),
        'close': prices
    }, index=dates)

    # Initialize backtest engine
    backtester = BacktestEngine(initial_capital=100000.0)

    # Run backtest with different execution qualities
    print("Running backtest with GOOD execution quality...")
    backtester.set_execution_quality(ExecutionQuality.GOOD)

    metrics = backtester.run_backtest(
        strategy_function=example_strategy,
        data=sample_data,
        symbol="NQ",
        position_size=1.0
    )

    # Print summary
    backtester.print_summary()