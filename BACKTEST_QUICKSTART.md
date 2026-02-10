# Backtest Section - Getting Started

## Quick Start (5 minutes)

### 1. Run the Web Interface
```bash
streamlit run app.py
```

Then navigate to the **"📈 Backtest"** tab.

### 2. Run a Single Backtest
1. Select your instrument (NQ or ES)
2. Choose a date range (e.g., 2024-01-01 to 2024-03-31)
3. Keep default balance ($10,000)
4. Click **"▶️ Run Single Backtest"**

### 3. View Results
- **Summary Metrics**: Final balance, return %, win rate, profit factor
- **Trade Statistics**: Number of wins/losses, average P&L
- **Risk Metrics**: Max drawdown, FTMO compliance check
- **Performance**: Sharpe ratio, monthly breakdown
- **Equity Curve**: Visual chart of account growth
- **Trade List**: All trades with entry/exit prices

### 4. Export Results
- Download as JSON (complete data)
- Download as CSV (trades only)
- Download as text report

## Python Command Line

### Option 1: Quick Example (Most Educational)
```bash
python quick_backtest_example.py
```

This runs several backtests and shows comparisons:
- NQ Q1 2024 backtest
- ES Q1 2024 backtest
- Walk-forward analysis
- FTMO compliance summary

### Option 2: Original Example Script
```bash
python example_backtest.py
```

Runs the original backtest with basic outputs.

### Option 3: Programmatic Usage
```python
from backtest_runner import BacktestRunner

runner = BacktestRunner(starting_balance=10000.0)

# Single backtest
result = runner.run_backtest(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

print(f"Return: {result.total_return_pct:.2f}%")
print(f"Win Rate: {result.win_rate:.1f}%")
print(f"Max Drawdown: {result.max_drawdown_pct:.2f}%")

# Walk-forward analysis
results = runner.run_walk_forward(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31",
    window_size_months=3
)

for i, r in enumerate(results, 1):
    print(f"Window {i}: {r.total_return_pct:.2f}% return")
```

## Understanding the Output

### Key Metrics for FTMO Compliance

| Metric | Target | What It Means |
|--------|--------|--------------|
| **Max Drawdown** | < 3.5% | Largest peak-to-trough loss |
| **Monthly Profit** | ≥ 5% | Average monthly returns |
| **Win Rate** | ≥ 50% | % of profitable trades |
| **Profit Factor** | > 1.0 | Wins ÷ Losses ratio |

### Performance Metrics

| Metric | Interpretation |
|--------|-----------------|
| **Sharpe Ratio** | Risk-adjusted returns (>1.0 is good) |
| **Sortino Ratio** | Downside risk-adjusted (>1.5 is good) |
| **Calmar Ratio** | Return per unit of drawdown |
| **Recovery Factor** | Profit ÷ Maximum Loss |

## Workflow: Training Your Bot

### Phase 1: Single Backtest (Hour 1)
1. Run backtest on recent 3-month period
2. Check if metrics meet FTMO targets
3. If results are poor, may need to adjust configuration
4. If results are good, proceed to Phase 2

### Phase 2: Extended Testing (Hour 2-3)
1. Test on different 3-month periods
2. Test on both NQ and ES
3. Save results for comparison
4. Look for consistency across periods

### Phase 3: Walk-Forward Validation (Hour 3-4)
1. Run walk-forward analysis on full year
2. Check if performance is stable across windows
3. Verify drawdown stays within limits
4. Ensure no "curve fitting" to single period

### Phase 4: Final Review
1. All results saved in Results Library
2. Compare metrics across all tests
3. Document findings
4. Ready for live trading!

## Interpreting Results

### Good Result Example
```
NQ Backtest Q1 2024:
✅ Return: 15.5% (>5% monthly target)
✅ Win Rate: 62% (>50% target)  
✅ Max Drawdown: 2.1% (<3.5% target)
✅ Profit Factor: 2.8 (>1.0 required)
✅ Sharpe Ratio: 1.8 (>1.0 good)
```

### Problem Example
```
NQ Backtest Q1 2024:
❌ Return: -3.2% (negative!)
⚠️  Win Rate: 45% (<50% target)
❌ Max Drawdown: 5.1% (>3.5% target)
❌ Profit Factor: 0.8 (<1.0 required)
❌ Sharpe Ratio: -0.5 (negative)
```
→ Strategy needs optimization

### Marginal Example
```
NQ Backtest Q1 2024:
⚠️  Return: 2.8% (<5% monthly target)
✅ Win Rate: 52% (just above target)
✅ Max Drawdown: 3.2% (just under target)
⚠️  Profit Factor: 1.1 (barely above 1.0)
⚠️  Sharpe Ratio: 0.8 (below 1.0 target)
```
→ Keep testing, watch for consistency

## Advanced Topics

### Walk-Forward Window Size
- **1-2 months**: More windows, finer-grained analysis
- **3 months**: Standard, good balance
- **6 months**: Fewer windows, broader view
- **12 months**: Single window, only for full-year tests

### Risk-Free Rate
The risk-free rate affects Sharpe/Sortino calculations:
- 4% = Current typical US Treasury yield
- 0% = Conservative, ignores risk-free alternatives
- Adjust if market conditions change

### Monthly P&L Breakdown
Shows which months were profitable:
- Consistent +P&L = Stable strategy
- Volatile +/- = Risky, curve-fitted
- Mostly losses = Strategy doesn't work

### Equity Curve Analysis
- Smooth uptrend = Healthy strategy
- Sharp drawdowns = Risky positions
- Flat sections = No trading opportunity
- Recovery after DD = Good risk management

## Troubleshooting

### "No trades executed"
- Check if date range includes trading days
- Verify market conditions allow setups
- Check if filters are too restrictive
- Ensure data is available for period

### "High drawdown (>5%)"
- Position sizing may be too aggressive
- Look for clustered losses
- Check for outlier trades
- Consider reducing risk per trade

### "Low win rate (<30%)"
- Many small winners can still profit
- Check profit factor > 1.0
- Review largest winning trades
- Ensure losses are cut quickly

### "Inconsistent across periods"
- Results vary wildly by quarter
- May indicate curve-fitting
- Try walk-forward analysis
- Consider reducing parameter complexity

## Files Generated

### In Web Interface
- `backtest_NQ_20240101.json` - Complete results data
- `trades_NQ_20240101.csv` - Trade-by-trade details
- `backtest_report_NQ_20240101.txt` - Summary report

### In Python (programmatic)
Results stored in `BacktestResult` object with:
- `result.to_dict()` - Convert to dictionary
- `result.equity_curve` - List of equity values
- `result.trades` - List of trade dicts
- All metrics accessible as attributes

## Next Steps

1. **Run backtests** on several date ranges
2. **Compare results** using Results Library
3. **Identify patterns** in good vs bad months
4. **Run walk-forward** to validate consistency
5. **Export results** for documentation
6. **Ready for trading!** 🚀

## Support & Documentation

- **BACKTEST_GUIDE.md** - Detailed metrics explanation
- **README.md** - Overall bot documentation
- **example_backtest.py** - Original example
- **quick_backtest_example.py** - Educational example
- **backtest_runner.py** - Source code with inline docs

## Tips for Success

1. **Start with 3-month windows** - Good balance of data
2. **Test both NQ and ES** - See which works better
3. **Save multiple runs** - Compare performance
4. **Check walk-forward** - Validate consistency
5. **Review trade details** - Understand what works
6. **Monitor drawdown** - Most important for FTMO
7. **Look for patterns** - Best months, market conditions
8. **Trust the process** - Backtests show promise, not guarantee

---

**Ready to train your bot?** Start with:
```bash
streamlit run app.py
```

Then go to **"📈 Backtest"** tab! 🎯
