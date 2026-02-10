"""
Quick Backtest Example
Simple script to demonstrate backtest functionality
"""

from backtest_runner import BacktestRunner
from datetime import datetime


def main():
    """Run example backtests."""
    
    print("=" * 80)
    print("FTMO TRADING BOT - BACKTEST RUNNER")
    print("=" * 80)
    print()
    
    # Initialize runner
    runner = BacktestRunner(starting_balance=10000.0)
    
    # Example 1: Single NQ backtest
    print("[1] Running single backtest: NQ (2024 Q1)")
    print("-" * 80)
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
    print()
    
    # Example 2: ES backtest
    print("[2] Running single backtest: ES (2024 Q1)")
    print("-" * 80)
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
    print()
    
    # Example 3: Comparison
    print("[3] Results Comparison")
    print("-" * 80)
    print(f"{'Metric':<30} {'NQ':<15} {'ES':<15}")
    print("-" * 60)
    print(f"{'Return %':<30} {result.total_return_pct:>14.2f}% {result_es.total_return_pct:>14.2f}%")
    print(f"{'Win Rate':<30} {result.win_rate:>14.1f}% {result_es.win_rate:>14.1f}%")
    print(f"{'Profit Factor':<30} {result.profit_factor:>14.2f}  {result_es.profit_factor:>14.2f}")
    print(f"{'Max Drawdown':<30} {result.max_drawdown_pct:>14.2f}% {result_es.max_drawdown_pct:>14.2f}%")
    print(f"{'Sharpe Ratio':<30} {result.sharpe_ratio:>14.2f}  {result_es.sharpe_ratio:>14.2f}")
    print()
    
    # Example 4: Walk-forward analysis
    print("[4] Running walk-forward analysis: NQ (2024 Full Year, 3m windows)")
    print("-" * 80)
    wf_results = runner.run_walk_forward(
        instrument="NQ",
        start_date="2024-01-01",
        end_date="2024-12-31",
        window_size_months=3
    )
    
    print(f"✓ Walk-forward analysis complete!")
    print(f"  Windows analyzed: {len(wf_results)}")
    print()
    print(f"{'Window':<10} {'Return %':<15} {'Win Rate':<15} {'Max DD %':<15} {'Sharpe':<10}")
    print("-" * 65)
    for i, wf_result in enumerate(wf_results, 1):
        print(f"{i:<10} {wf_result.total_return_pct:>14.2f}% {wf_result.win_rate:>14.1f}% {wf_result.max_drawdown_pct:>14.2f}% {wf_result.sharpe_ratio:>9.2f}")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # FTMO Compliance Check
    print("\n[FTMO Compliance Check]")
    compliance = []
    
    # Check NQ results
    print("\nNQ Results:")
    dd_check = "✅ PASS" if abs(result.max_drawdown_pct) < 3.5 else "❌ FAIL"
    print(f"  Max Drawdown < 3.5%:    {abs(result.max_drawdown_pct):.2f}% {dd_check}")
    compliance.append(abs(result.max_drawdown_pct) < 3.5)
    
    monthly_return_est = result.total_return_pct / 3  # Rough quarterly estimate
    monthly_check = "✅ PASS" if monthly_return_est >= 5.0 else "⚠️  BELOW TARGET"
    print(f"  Monthly Profit Target:  {monthly_return_est:.2f}% {monthly_check}")
    compliance.append(monthly_return_est >= 5.0)
    
    profit_factor_check = "✅ PASS" if result.profit_factor > 1.0 else "❌ FAIL"
    print(f"  Profit Factor > 1.0:    {result.profit_factor:.2f} {profit_factor_check}")
    compliance.append(result.profit_factor > 1.0)
    
    # Check ES results
    print("\nES Results:")
    dd_check_es = "✅ PASS" if abs(result_es.max_drawdown_pct) < 3.5 else "❌ FAIL"
    print(f"  Max Drawdown < 3.5%:    {abs(result_es.max_drawdown_pct):.2f}% {dd_check_es}")
    compliance.append(abs(result_es.max_drawdown_pct) < 3.5)
    
    monthly_return_est_es = result_es.total_return_pct / 3
    monthly_check_es = "✅ PASS" if monthly_return_est_es >= 5.0 else "⚠️  BELOW TARGET"
    print(f"  Monthly Profit Target:  {monthly_return_est_es:.2f}% {monthly_check_es}")
    compliance.append(monthly_return_est_es >= 5.0)
    
    profit_factor_check_es = "✅ PASS" if result_es.profit_factor > 1.0 else "❌ FAIL"
    print(f"  Profit Factor > 1.0:    {result_es.profit_factor:.2f} {profit_factor_check_es}")
    compliance.append(result_es.profit_factor > 1.0)
    
    # Overall status
    print("\n[Overall Status]")
    if all(compliance):
        print("✅ ALL CHECKS PASSED - Strategy meets FTMO requirements!")
    else:
        print("⚠️  Some checks failed or below targets - consider optimization")
    
    print("\n" + "=" * 80)
    print("Use the Streamlit web interface for more detailed analysis:")
    print("  streamlit run app.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
