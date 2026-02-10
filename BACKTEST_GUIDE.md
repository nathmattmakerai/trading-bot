# Backtest Guide - FTMO Trading Bot

## Overview

The backtest section provides comprehensive historical data testing capabilities to train and validate your trading bot strategy. You can run single backtests, walk-forward analysis, and save results for comparison.

## Features

### 1. Single Backtest
Run a complete backtest on any historical period with detailed performance metrics.

**Inputs:**
- **Instrument**: NQ (Nasdaq-100) or ES (S&P 500)
- **Start Date**: Beginning of backtest period
- **End Date**: End of backtest period
- **Starting Balance**: Initial account capital
- **Risk-Free Rate**: For Sharpe/Sortino calculations

**Outputs - Summary Metrics:**
- Final Balance & Total P&L
- Return Percentage
- Win Rate & Profit Factor

**Outputs - Detailed Tabs:**

#### Trade Statistics
- Total, Winning, Losing trades
- Win/Loss rate percentages
- Average Win/Loss amounts
- Largest Win/Loss amounts
- Total Wins and Losses P&L

#### Risk Metrics
- **Max Drawdown %**: Largest peak-to-trough decline
- **Max Drawdown Amount**: Dollar value of largest drawdown
- **Drawdown Duration**: Number of bars during worst drawdown
- FTMO Compliance Check (< 3.5% target)

#### Performance Metrics
- **Sharpe Ratio**: Risk-adjusted returns (higher = better)
- **Sortino Ratio**: Downside risk-adjusted returns
- **Calmar Ratio**: Return divided by maximum drawdown
- **Recovery Factor**: Total profit divided by max loss
- **Monthly P&L Breakdown**: Chart of monthly performance

#### Equity Curve
- Visual representation of account growth
- Shows all trades with running balance
- Reference line at starting balance

#### Trade List
- Complete list of all executed trades
- Entry/exit prices and dates
- P&L and % return per trade
- Exit reason (TP, SL, or session end)

#### Export Options
- **JSON**: Complete results data
- **CSV**: Trade-by-trade details
- **Text Report**: Summary report format

### 2. Walk-Forward Analysis

Tests your strategy on sequential non-overlapping periods for more robust validation.

**Process:**
1. Divide full period into multiple windows
2. Run backtest on each window independently
3. Compare results across windows
4. Identify consistent vs. inconsistent performance

**Configuration:**
- Same instrument selection as single backtest
- Window Size: 1-12 months (typically 3 months)
- Larger windows = fewer, longer tests
- Smaller windows = more, shorter tests

**Output:**
- Summary statistics (avg return, avg drawdown, avg Sharpe)
- Window-by-window results table
- Allows you to see if strategy is stable across different market conditions

### 3. Results Library

Save and compare multiple backtest runs.

**Features:**
- Name your backtest results
- Automatic timestamp recording
- Side-by-side metric comparison
- Delete results to keep library clean

## Backtest Metrics Explained

### Trade Statistics

| Metric | Meaning | Formula |
|--------|---------|---------|
| Win Rate | % of profitable trades | (Wins / Total Trades) × 100 |
| Profit Factor | Gross profit to gross loss ratio | Total Wins / Total Losses |
| Avg Win/Loss | Average P&L per winning/losing trade | Sum of Wins/Losses / Count |
| Largest Win/Loss | Best and worst single trade | Max/Min trade P&L |

### Risk Metrics

| Metric | Meaning | Interpretation |
|--------|---------|-----------------|
| Max Drawdown | Largest peak-to-trough decline | Lower is better; <3.5% for FTMO |
| Drawdown Duration | How long it took to recover | Fewer bars = quicker recovery |

### Performance Metrics

| Metric | Formula | Good Value |
|--------|---------|-----------|
| Sharpe Ratio | (Return - Risk Free) / StdDev | > 1.0 |
| Sortino Ratio | (Return - Risk Free) / DownsideStdDev | > 1.5 |
| Calmar Ratio | Annual Return / Max Drawdown | > 1.0 |
| Recovery Factor | Total Profit / Max Loss | > 2.0 |

## Workflow Example

### Step 1: Run Initial Backtest
1. Go to "📈 Backtest" → "Single Backtest"
2. Set dates to cover 3-6 months
3. Keep default balance ($10,000)
4. Click "Run Single Backtest"

### Step 2: Analyze Results
1. Check Summary Metrics (win rate, return %)
2. Review Risk Metrics (drawdown < 3.5%?)
3. Check Performance metrics (Sharpe > 1.0?)
4. Review Trade List for patterns

### Step 3: Save Results
1. Enter a descriptive name (e.g., "NQ Q1 2024")
2. Click "Save Result"
3. Results stored in session for comparison

### Step 4: Run Multiple Tests
1. Test different date ranges
2. Test different instruments (NQ vs ES)
3. Save each result for comparison

### Step 5: Walk-Forward Test
1. If single tests look good, run walk-forward
2. Validates strategy across multiple periods
3. Checks for stability and consistency

## FTMO Compliance Targets

Your backtest should target these FTMO guidelines:

| Metric | Target | Your Result |
|--------|--------|------------|
| Max Daily Loss | < 2.5% | — |
| Max Drawdown | < 3.5% | — |
| Monthly Profit | ≥ 5% | — |
| Win Rate | ≥ 50% | — |

## Tips for Better Results

1. **Test on Recent Data**: Use recent 6-12 months to reflect current market conditions
2. **Vary Instruments**: Test both NQ and ES to see differences
3. **Check Walk-Forward**: Single success doesn't guarantee future results
4. **Review Trade Details**: Look for patterns in winning vs losing trades
5. **Monitor Drawdown**: Max drawdown is key for FTMO compliance
6. **Compare Metrics**: Use Results Library to compare different test runs

## Common Issues

### No Trades Executed
- Check if date range includes trading days
- Verify market conditions allow setups (compression + breakout)
- Check if filters are too restrictive (macro, calendar)

### High Drawdown
- May indicate over-leveraging in position sizing
- Consider reducing risk per trade
- Look for clustering of losses

### Low Win Rate but Positive P&L
- Larger winners compensate for more losers
- Profit Factor > 1.0 is what matters
- Consistency of wins matters more than count

## Python API Usage

You can also run backtests programmatically:

```python
from backtest_runner import BacktestRunner

# Initialize runner
runner = BacktestRunner(starting_balance=10000.0)

# Run single backtest
result = runner.run_backtest(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# Access results
print(f"Return: {result.total_return_pct:.2f}%")
print(f"Win Rate: {result.win_rate:.1f}%")
print(f"Max Drawdown: {result.max_drawdown_pct:.2f}%")
print(f"Sharpe Ratio: {result.sharpe_ratio:.2f}")

# Run walk-forward analysis
results = runner.run_walk_forward(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31",
    window_size_months=3
)

# Compare windows
for i, result in enumerate(results, 1):
    print(f"Window {i}: {result.total_return_pct:.2f}%")
```

## Advanced Analysis

### Custom Metrics
Modify `backtest_runner.py` to add custom performance metrics:

```python
class BacktestAnalyzer:
    def compute_custom_metric(self, trades, equity_curve):
        # Your custom calculation here
        pass
```

### Parameter Optimization
Extend the `run_parameter_optimization` method to test different strategy parameters:

```python
runner.run_parameter_optimization(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31",
    parameter_ranges={
        "atr_period": [10, 14, 20],
        "risk_per_trade": [0.5, 0.75, 1.0],
    }
)
```

## Export and Reporting

### JSON Export
Complete results data for further analysis or import into other tools.

### CSV Export
Trade-by-trade details for Excel analysis or charting.

### Text Report
Summary report suitable for review or archive.

---

**Last Updated**: February 2026
**Version**: PRD v1 FROZEN
**Status**: Production Ready
