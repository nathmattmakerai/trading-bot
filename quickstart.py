#!/usr/bin/env python3
"""
QUICK START GUIDE - FTMO Futures Bot

Exécute ceci pour démarrer immédiatement.
"""

import sys
import os

# Add repo to path
sys.path.insert(0, os.path.dirname(__file__))


def main():
    """Quick start."""
    
    print("\n" + "="*80)
    print("FTMO FUTURES BOT - QUICK START")
    print("="*80 + "\n")
    
    # Step 1: Import
    print("Step 1: Importing modules...")
    try:
        from main import TradingBot
        from config.rules_v1 import VERSION, LOCKED
        print(f"✓ Imports successful (v{VERSION}, Locked: {LOCKED})\n")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("  Run: pip install -r requirements.txt")
        return 1
    
    # Step 2: Initialize
    print("Step 2: Initializing bot...")
    try:
        bot = TradingBot(starting_balance=10000.0)
        print("✓ Bot initialized with $10,000\n")
    except Exception as e:
        print(f"✗ Init error: {e}")
        return 1
    
    # Step 3: Show configuration
    print("Step 3: Configuration:")
    print("-" * 80)
    print(f"  Timeframe:           {bot.rules['compression']['atr_period']} (15m)")
    print(f"  Compression ATR:     < 0.75 × ATR(50)")
    print(f"  Risk per trade:      {bot.rules['risk']['risk_per_trade']*100:.2f}%")
    print(f"  Max daily loss:      {bot.rules['risk']['max_daily_loss']*100:.2f}%")
    print(f"  Max trades/day:      {bot.rules['risk']['max_trades_per_day']}")
    print(f"  TP ratio:            {bot.rules['position']['take_profit_ratio']}R (fixe)")
    print(f"  VIX risk-on:         < {bot.rules['macro']['risk_on_vix']}")
    print(f"  VIX risk-off:        > {bot.rules['macro']['risk_off_vix']}")
    print(f"  RTH session:         8:00 AM - 3:00 PM ET")
    print("-" * 80 + "\n")
    
    # Step 4: Quick test
    print("Step 4: Running quick test...")
    try:
        # Test compression detector
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range("2025-01-01", periods=100, freq="15min")
        np.random.seed(42)
        
        closes = np.random.normal(100, 0.1, 100).cumsum() + 100
        df_test = pd.DataFrame({
            "open": closes,
            "high": closes + np.random.uniform(0, 0.05, 100),
            "low": closes - np.random.uniform(0, 0.05, 100),
            "close": closes,
            "volume": np.random.randint(100000, 500000, 100),
        }, index=dates)
        
        is_comp = bot.compression_detector.is_compression(df_test)
        print(f"  Compression detected: {is_comp}")
        
        signal = bot.breakout_setup.get_breakout_signal(df_test)
        print(f"  Breakout signal: {signal}")
        
        print("✓ Quick test passed\n")
    
    except Exception as e:
        print(f"✗ Test error: {e}")
        return 1
    
    # Step 5: Next steps
    print("Step 5: Next steps:")
    print("-" * 80)
    print("1. Run full backtest:")
    print("   python example_backtest.py")
    print()
    print("2. Run unit tests:")
    print("   python -m pytest tests/validation_suite.py -v")
    print()
    print("3. Read documentation:")
    print("   - README.md (setup & usage)")
    print("   - TECHNICAL_DOCS.md (deep dive)")
    print("   - IMPLEMENTATION_SUMMARY.md (overview)")
    print()
    print("4. Start backtesting:")
    print("   from main import TradingBot")
    print("   bot = TradingBot(starting_balance=10000)")
    print("   stats = bot.backtest('NQ', '2024-01-01', '2024-12-31')")
    print("-" * 80 + "\n")
    
    print("="*80)
    print("✓ Quick start complete! Ready for development.")
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
