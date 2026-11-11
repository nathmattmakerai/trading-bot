# Backtesting Module

This module implements realistic backtesting with transaction costs, slippage, and execution quality to ensure backtest results are representative of real trading conditions.

## Features

- **Realistic Execution Simulation**: Incorporates transaction costs and slippage in trade execution
- **Multiple Execution Quality Levels**: Perfect, Good, Fair, and Poor execution quality settings
- **Comprehensive Metrics**: Calculates detailed performance metrics including Sharpe ratio and max drawdown
- **Trade History Tracking**: Records all executed trades with full details
- **Portfolio Value Tracking**: Monitors portfolio value over time

## Core Components

### BacktestEngine
The main class that handles backtesting with realistic execution parameters.

### TradeResult
Data class representing the result of a single trade with all relevant details.

### ExecutionQuality
Enumeration for different execution quality levels (Perfect, Good, Fair, Poor).

### BacktestMetrics
Container for performance metrics calculated from backtest results.

## Key Capabilities

1. **Transaction Costs**: Calculates costs based on trade value and configured rates
2. **Slippage Modeling**: Simulates price impact due to market liquidity
3. **Multiple Quality Levels**: Adjusts costs and slippage based on execution quality
4. **Performance Metrics**: Comprehensive analysis including:
   - Total return and annualized return
   - Sharpe ratio for risk-adjusted returns
   - Maximum drawdown
   - Win rate and average win/loss
   - Transaction and slippage cost tracking

## Usage

```python
from backtest_engine import BacktestEngine, ExecutionQuality

# Initialize backtest engine
backtester = BacktestEngine(initial_capital=100000.0)

# Set execution quality (GOOD is default)
backtester.set_execution_quality(ExecutionQuality.GOOD)

# Run backtest with your strategy
metrics = backtester.run_backtest(
    strategy_function=my_strategy,
    data=historical_data,
    symbol="NQ",
    position_size=1.0
)

# Print results
backtester.print_summary()
```

## Testing

Run unit tests with:
```bash
python -m unittest backtesting/test_backtest_engine.py
```