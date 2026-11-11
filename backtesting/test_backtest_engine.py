"""
Unit tests for Backtest Engine
"""

import unittest
import pandas as pd
import numpy as np
from backtest_engine import BacktestEngine, ExecutionQuality, TradeResult

class TestBacktestEngine(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.backtester = BacktestEngine(initial_capital=100000.0)

    def test_initialization(self):
        """Test that the backtest engine initializes correctly."""
        self.assertEqual(self.backtester.initial_capital, 100000.0)
        self.assertEqual(self.backtester.current_capital, 100000.0)
        self.assertEqual(len(self.backtester.trades), 0)
        self.assertEqual(len(self.backtester.portfolio_history), 0)

    def test_execution_quality_setting(self):
        """Test setting different execution qualities."""
        # Test perfect quality
        self.backtester.set_execution_quality(ExecutionQuality.PERFECT)
        self.assertEqual(self.backtester.transaction_cost_rate, 0.0)
        self.assertEqual(self.backtester.slippage_rate, 0.0)

        # Test good quality
        self.backtester.set_execution_quality(ExecutionQuality.GOOD)
        self.assertEqual(self.backtester.transaction_cost_rate, 0.001)
        self.assertEqual(self.backtester.slippage_rate, 0.0005)

    def test_transaction_cost_calculation(self):
        """Test transaction cost calculation."""
        self.backtester.set_execution_quality(ExecutionQuality.GOOD)

        cost = self.backtester.calculate_transaction_costs(price=18000.0, quantity=1.0)
        expected_cost = 18000.0 * 1.0 * 0.001
        self.assertEqual(cost, expected_cost)

    def test_slippage_calculation(self):
        """Test slippage calculation."""
        self.backtester.set_execution_quality(ExecutionQuality.GOOD)

        slippage = self.backtester.calculate_slippage(price=18000.0, quantity=1.0)
        expected_slippage = 18000.0 * 1.0 * 0.0005
        self.assertEqual(slippage, expected_slippage)

    def test_trade_execution(self):
        """Test trade execution with costs."""
        # Set good execution quality
        self.backtester.set_execution_quality(ExecutionQuality.GOOD)

        # Execute a simple trade
        result = self.backtester.simulate_trade_execution(
            symbol="NQ",
            entry_price=18000.0,
            exit_price=18100.0,
            quantity=1.0,
            side='long',
            entry_time=pd.Timestamp('2023-01-01'),
            exit_time=pd.Timestamp('2023-01-02')
        )

        # Verify result
        self.assertEqual(result.symbol, "NQ")
        self.assertEqual(result.entry_price, 18000.0)
        self.assertEqual(result.exit_price, 18100.0)
        self.assertEqual(result.quantity, 1.0)
        self.assertEqual(result.side, 'long')
        self.assertIsNotNone(result.profit_loss)
        self.assertGreater(result.profit_loss, 0)  # Should be positive profit

    def test_empty_trades(self):
        """Test metrics calculation with no trades."""
        metrics = self.backtester._calculate_metrics()

        self.assertEqual(metrics.total_return, 0.0)
        self.assertEqual(metrics.total_trades, 0)
        self.assertEqual(metrics.win_rate, 0.0)

    def test_portfolio_history_tracking(self):
        """Test that portfolio history is tracked correctly."""
        # Set good execution quality
        self.backtester.set_execution_quality(ExecutionQuality.GOOD)

        # Execute a trade to populate history
        result = self.backtester.simulate_trade_execution(
            symbol="NQ",
            entry_price=18000.0,
            exit_price=18100.0,
            quantity=1.0,
            side='long',
            entry_time=pd.Timestamp('2023-01-01'),
            exit_time=pd.Timestamp('2023-01-02')
        )

        # Should have at least one history record
        self.assertGreaterEqual(len(self.backtester.portfolio_history), 1)

if __name__ == '__main__':
    unittest.main()