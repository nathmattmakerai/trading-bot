"""
Integration example showing how BacktestEngine works with RiskEngine
"""

import pandas as pd
import numpy as np
from backtest_engine import BacktestEngine, ExecutionQuality
from risk.risk_engine import RiskEngine

# Example strategy function that works with both systems
def integrated_strategy(data):
    """
    Strategy that considers both market data and risk parameters

    Args:
        data (pd.Series): Price data

    Returns:
        str: Trading signal
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

def example_integration():
    """Demonstrate integration between backtest engine and risk engine"""

    print("=== BACKTESTING WITH RISK INTEGRATION EXAMPLE ===")

    # Create sample market data
    dates = pd.date_range('2023-01-01', periods=50, freq='D')
    prices = 18000 + np.cumsum(np.random.randn(50) * 50)

    sample_data = pd.DataFrame({
        'open': prices,
        'high': prices + np.abs(np.random.randn(50) * 30),
        'low': prices - np.abs(np.random.randn(50) * 30),
        'close': prices
    }, index=dates)

    # Initialize both engines
    risk_engine = RiskEngine(initial_equity=100000.0)
    backtester = BacktestEngine(initial_capital=100000.0)

    print("Risk Engine initialized")
    print("Backtest Engine initialized")

    # Set execution quality to realistic level
    backtester.set_execution_quality(ExecutionQuality.GOOD)

    # Run backtest
    print("\nRunning backtest with integrated risk considerations...")
    metrics = backtester.run_backtest(
        strategy_function=integrated_strategy,
        data=sample_data,
        symbol="NQ",
        position_size=1.0
    )

    # Display results
    print("\n=== BACKTEST RESULTS ===")
    print(f"Total Return: {metrics.total_return*100:.2f}%")
    print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
    print(f"Total Trades: {metrics.total_trades}")
    print(f"Win Rate: {metrics.win_rate*100:.2f}%")
    print(f"Total Transaction Costs: ${metrics.total_transaction_costs:,.2f}")
    print(f"Total Slippage Costs: ${metrics.total_slippage_costs:,.2f}")

    # Show risk metrics
    print("\n=== RISK METRICS ===")
    risk_metrics = risk_engine.get_risk_metrics()
    for key, value in risk_metrics.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    example_integration()