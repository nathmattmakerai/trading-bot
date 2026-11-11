"""
Demo script for data collection and backtesting.
This script demonstrates how to use the crawler and backtesting system.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.crawler import FinancialDataCrawler
from data.stock_data_loader import StockDataLoader
from data.futures_data_loader import FuturesDataLoader
from data.macro_data_loader import MacroDataLoader
from backtest_runner import BacktestRunner

def demo_crawler():
    """Demonstrate the crawler functionality."""
    print("=" * 80)
    print("DEMO: Financial Data Crawler")
    print("=" * 80)

    # Initialize crawler
    crawler = FinancialDataCrawler()

    # Test stock data collection
    print("\n1. Collecting stock data...")
    stocks = crawler.crawl_stock_data(period="6mo")
    print(f"✓ Retrieved {len(stocks)} stocks")

    # Test crypto data collection
    print("\n2. Collecting crypto data...")
    crypto = crawler.crawl_crypto_data(period="6mo")
    print(f"✓ Retrieved {len(crypto)} cryptos")

    # Test futures data collection
    print("\n3. Collecting futures data...")
    futures = crawler.crawl_futures_data(period="6mo")
    print(f"✓ Retrieved {len(futures)} futures")

    # Test sentiment data collection
    print("\n4. Collecting market sentiment...")
    sentiment = crawler.crawl_market_sentiment()
    print("✓ Market sentiment data collected")

    # Test technical indicators
    print("\n5. Collecting technical indicators...")
    if stocks:
        ticker = list(stocks.keys())[0]
        indicators = crawler.crawl_technical_indicators(ticker, period="6mo")
        print(f"✓ Technical indicators retrieved for {ticker}")

    # Save data to file
    print("\n6. Saving collected data...")
    all_data = {
        'stocks': stocks,
        'crypto': crypto,
        'futures': futures,
        'sentiment': sentiment,
        'indicators': indicators if 'indicators' in locals() else {}
    }

    crawler.save_data(all_data, 'demo_collected_data.json')
    print("✓ Data saved to demo_collected_data.json")

    return all_data

def demo_backtesting():
    """Demonstrate backtesting functionality."""
    print("\n" + "=" * 80)
    print("DEMO: Backtesting System")
    print("=" * 80)

    # Initialize runner
    runner = BacktestRunner(starting_balance=10000.0)

    # Run example backtests
    print("\n[1] Running single backtest: NQ (2024 Q1)")
    result = runner.run_backtest(
        instrument="NQ",
        start_date="2024-01-01",
        end_date="2024-03-31",
    )

    print(f"✓ Backtest complete!")
    print(f"  Starting Balance: ${result.starting_balance:,.2f}")
    print(f"  Final Balance:    ${result.final_balance:,.2f}")
    print(f"  Total P&L:        ${result.total_pnl:,.2f}")
    print(f"  Return:           {result.total_return_pct:.2f}%")
    print(f"  Total Trades:     {result.num_trades}")
    print(f"  Win Rate:         {result.win_rate:.1f}%")
    print(f"  Max Drawdown:     {result.max_drawdown_pct:.2f}%")
    print(f"  Profit Factor:    {result.profit_factor:.2f}")
    print(f"  Sharpe Ratio:     {result.sharpe_ratio:.2f}")

    # Run ES backtest
    print("\n[2] Running single backtest: ES (2024 Q1)")
    result_es = runner.run_backtest(
        instrument="ES",
        start_date="2024-01-01",
        end_date="2024-03-31",
    )

    print(f"✓ Backtest complete!")
    print(f"  Return:           {result_es.total_return_pct:.2f}%")
    print(f"  Total Trades:     {result_es.num_trades}")
    print(f"  Win Rate:         {result_es.win_rate:.1f}%")
    print(f"  Max Drawdown:     {result_es.max_drawdown_pct:.2f}%")

    # Run walk-forward analysis
    print("\n[3] Running walk-forward analysis: NQ (2024 Full Year, 3m windows)")
    wf_results = runner.run_walk_forward(
        instrument="NQ",
        start_date="2024-01-01",
        end_date="2024-12-31",
        window_size_months=3
    )

    print(f"✓ Walk-forward analysis complete!")
    print(f"  Windows analyzed: {len(wf_results)}")

    return result, result_es, wf_results

def demo_integration():
    """Demonstrate integration between crawler and backtesting."""
    print("\n" + "=" * 80)
    print("DEMO: Crawler + Backtesting Integration")
    print("=" * 80)

    # First collect data
    print("\n1. Collecting financial data...")
    data = demo_crawler()

    # Then run backtest using collected data
    print("\n2. Running backtest with collected data...")
    result, result_es, wf_results = demo_backtesting()

    print("\n" + "=" * 80)
    print("INTEGRATION DEMO COMPLETE")
    print("=" * 80)
    print("\nThis demonstrates how the crawler can collect data for backtesting.")
    print("The system is designed to be extensible and modular.")

if __name__ == "__main__":
    demo_integration()