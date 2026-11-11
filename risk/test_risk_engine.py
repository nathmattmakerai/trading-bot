"""
Unit tests for Risk Engine
"""

import unittest
from risk_engine import RiskEngine, RiskParameters, RiskStatus

class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.risk_engine = RiskEngine(initial_equity=100000.0)

    def test_initialization(self):
        """Test that the risk engine initializes correctly."""
        self.assertEqual(self.risk_engine.current_equity, 100000.0)
        self.assertEqual(self.risk_engine.initial_equity, 100000.0)
        self.assertEqual(len(self.risk_engine.positions), 0)
        self.assertEqual(len(self.risk_engine.trade_history), 0)

    def test_position_sizing(self):
        """Test position sizing calculations."""
        position_size, risk_amount = self.risk_engine.calculate_position_size(
            symbol="NQ",
            entry_price=18000.0,
            stop_loss_distance=50.0
        )

        # Should calculate a reasonable position size
        self.assertGreater(position_size, 0)
        self.assertGreater(risk_amount, 0)

    def test_trade_validation_acceptable(self):
        """Test that acceptable trades are validated correctly."""
        status = self.risk_engine.validate_trade(
            symbol="NQ",
            entry_price=18000.0,
            stop_loss_distance=50.0
        )

        self.assertEqual(status, RiskStatus.ACCEPTABLE)

    def test_execute_trade(self):
        """Test executing a trade."""
        position_size, _ = self.risk_engine.calculate_position_size(
            symbol="NQ",
            entry_price=18000.0,
            stop_loss_distance=50.0
        )

        success = self.risk_engine.execute_trade(
            symbol="NQ",
            entry_price=18000.0,
            stop_loss_distance=50.0,
            quantity=position_size
        )

        self.assertTrue(success)
        self.assertEqual(len(self.risk_engine.positions), 1)

    def test_get_risk_metrics(self):
        """Test getting risk metrics."""
        metrics = self.risk_engine.get_risk_metrics()

        self.assertIn('current_equity', metrics)
        self.assertIn('initial_equity', metrics)
        self.assertIn('daily_loss', metrics)
        self.assertIn('total_risk_exposure', metrics)
        self.assertIn('risk_ratio', metrics)
        self.assertIn('position_count', metrics)

    def test_update_equity(self):
        """Test updating equity."""
        initial_equity = self.risk_engine.current_equity
        self.risk_engine.update_equity(120000.0)

        self.assertEqual(self.risk_engine.current_equity, 120000.0)

    def test_reset_daily_metrics(self):
        """Test resetting daily metrics."""
        self.risk_engine.reset_daily_metrics()

        self.assertEqual(self.risk_engine.daily_loss, 0.0)

if __name__ == '__main__':
    unittest.main()