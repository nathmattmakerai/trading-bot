"""
Script d'exemple: Lancer un backtest complet.
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
from main import TradingBot


def main():
    """Main execution."""
    print("=" * 80)
    print("FTMO FUTURES BOT - PRD v1 (FROZEN)")
    print("=" * 80)
    print()
    
    # Initialize bot
    print("[1] Initializing bot...")
    bot = TradingBot(starting_balance=10000.0)
    print("✓ Bot initialized with $10,000 starting balance")
    print()
    
    # Run backtest
    print("[2] Running backtest NQ (2024-01-01 to 2024-12-31)...")
    try:
        stats = bot.backtest(
            instrument="NQ",
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
        
        print()
        print("[3] Backtest Results:")
        print("-" * 80)
        print(f"Starting Balance:      ${stats.get('starting_balance', 0):,.2f}")
        print(f"Final Balance:         ${stats.get('final_balance', 0):,.2f}")
        print(f"Total PnL:             ${stats.get('total_pnl', 0):,.2f}")
        print(f"Total Return:          {stats.get('total_return_pct', 0):.2f}%")
        print()
        print(f"Total Trades:          {stats.get('num_trades', 0)}")
        print(f"Winning Trades:        {stats.get('num_wins', 0)}")
        print(f"Losing Trades:         {stats.get('num_losses', 0)}")
        print(f"Win Rate:              {stats.get('win_rate', 0):.1f}%")
        print()
        print(f"Average Win:           ${stats.get('avg_win', 0):,.2f}")
        print(f"Average Loss:          ${stats.get('avg_loss', 0):,.2f}")
        print(f"Largest Win:           ${stats.get('largest_win', 0):,.2f}")
        print(f"Largest Loss:          ${stats.get('largest_loss', 0):,.2f}")
        print()
        print(f"Max Drawdown:          {stats.get('max_drawdown_pct', 0):.2f}%")
        print("-" * 80)
        
        # Validate KPI targets
        print()
        print("[4] KPI Target Validation:")
        print("-" * 80)
        
        max_dd_target = 3.5
        max_dd_actual = abs(stats.get('max_drawdown_pct', 0))
        dd_status = "✓ PASS" if max_dd_actual < max_dd_target else "✗ FAIL"
        print(f"Max Drawdown < 3.5%:   {max_dd_actual:.2f}% {dd_status}")
        
        monthly_return_target = 5.0
        # Rough estimate: annual return / 12
        monthly_return_est = stats.get('total_return_pct', 0) / 12
        monthly_status = "✓ PASS" if monthly_return_est >= monthly_return_target else "✗ FAIL"
        print(f"Monthly Return ≥ 5%:   {monthly_return_est:.2f}% {monthly_status}")
        
        print("-" * 80)
        
        # Get equity curve
        print()
        print("[5] Equity Curve:")
        equity_df = bot.backtest_engine.get_equity_curve()
        
        if len(equity_df) > 0:
            print(f"Total data points:     {len(equity_df)}")
            print(f"Start equity:          ${equity_df['equity'].iloc[0]:,.2f}")
            print(f"End equity:            ${equity_df['equity'].iloc[-1]:,.2f}")
            
            # Optionally plot
            try:
                plt.figure(figsize=(12, 6))
                plt.plot(equity_df.index, equity_df['equity'], label='Equity', linewidth=2)
                plt.xlabel('Date')
                plt.ylabel('Equity ($)')
                plt.title('FTMO Futures Bot - Equity Curve')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig('equity_curve.png', dpi=150)
                print("✓ Equity curve saved as 'equity_curve.png'")
            except Exception as e:
                print(f"Note: Could not plot equity curve ({e})")
        else:
            print("No closed trades (equity curve empty)")
        
        print()
        print("=" * 80)
        print("Backtest complete!")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"✗ Error during backtest: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
