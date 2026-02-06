"""
Tests unitaires pour validation système.
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from engine.filters.macro_filter import MacroFilter, RiskRegime
from engine.filters.calendar_filter import CalendarFilter
from engine.filters.session_filter import SessionFilter
from engine.structure.compression_detector import CompressionDetector
from engine.setup.breakout_v1 import BreakoutSetupV1
from engine.risk.position_sizer import PositionSizer


class TestMacroFilter(unittest.TestCase):
    """Tests filtre macro."""
    
    def setUp(self):
        self.macro_filter = MacroFilter()
    
    def test_risk_on_regime(self):
        """VIX < 18 = risk-on."""
        regime = self.macro_filter.get_risk_regime(vix=15.0, us10y_yield=4.0)
        self.assertEqual(regime, RiskRegime.RISK_ON)
    
    def test_risk_off_regime(self):
        """VIX > 22 = risk-off."""
        regime = self.macro_filter.get_risk_regime(vix=25.0, us10y_yield=4.0)
        self.assertEqual(regime, RiskRegime.RISK_OFF)
    
    def test_neutral_regime(self):
        """18 < VIX < 22 = neutral."""
        regime = self.macro_filter.get_risk_regime(vix=20.0, us10y_yield=4.0)
        self.assertEqual(regime, RiskRegime.NEUTRAL)
    
    def test_long_allowed_in_risk_on(self):
        """Long autorisé en risk-on."""
        self.assertTrue(
            self.macro_filter.is_long_allowed(RiskRegime.RISK_ON)
        )
    
    def test_long_not_allowed_in_risk_off(self):
        """Long non autorisé en risk-off."""
        self.assertFalse(
            self.macro_filter.is_long_allowed(RiskRegime.RISK_OFF)
        )
    
    def test_should_trade_long(self):
        """Long trade validation."""
        regime = RiskRegime.RISK_ON
        self.assertTrue(self.macro_filter.should_trade(regime, "long"))
    
    def test_should_not_trade_long_in_risk_off(self):
        """Long trade bloquée en risk-off."""
        regime = RiskRegime.RISK_OFF
        self.assertFalse(self.macro_filter.should_trade(regime, "long"))


class TestCalendarFilter(unittest.TestCase):
    """Tests filtre calendrier."""
    
    def setUp(self):
        self.calendar_filter = CalendarFilter()
    
    def test_fomc_blackout(self):
        """FOMC date est en blackout."""
        fomc_date = pd.to_datetime("2025-01-29")
        self.assertTrue(self.calendar_filter.is_blackout_date(fomc_date))
    
    def test_nfp_blackout(self):
        """NFP date est en blackout."""
        nfp_date = pd.to_datetime("2025-01-10")
        self.assertTrue(self.calendar_filter.is_blackout_date(nfp_date))
    
    def test_normal_day_not_blackout(self):
        """Jour normal n'est pas en blackout."""
        normal_date = pd.to_datetime("2025-01-06")
        self.assertFalse(self.calendar_filter.is_blackout_date(normal_date))
    
    def test_buffer_day_before_event(self):
        """Jour avant événement est en blackout (buffer)."""
        fomc_date = pd.to_datetime("2025-01-29")
        day_before = fomc_date - timedelta(days=1)
        self.assertTrue(self.calendar_filter.is_blackout_date(day_before))


class TestSessionFilter(unittest.TestCase):
    """Tests filtre session."""
    
    def setUp(self):
        self.session_filter = SessionFilter()
    
    def test_rth_open_is_valid(self):
        """8:30 AM ET = dans RTH."""
        ts = pd.Timestamp("2025-01-06 13:30:00", tz="UTC")
        self.assertTrue(self.session_filter.is_rth_session(ts))
    
    def test_premarket_is_invalid(self):
        """7:00 AM ET = prémarché (invalid)."""
        ts = pd.Timestamp("2025-01-06 12:00:00", tz="UTC")
        self.assertFalse(self.session_filter.is_rth_session(ts))
    
    def test_postmarket_is_invalid(self):
        """4:00 PM ET = postmarché (invalid)."""
        ts = pd.Timestamp("2025-01-06 21:00:00", tz="UTC")
        self.assertFalse(self.session_filter.is_rth_session(ts))
    
    def test_rth_close_is_boundary(self):
        """3:00 PM ET = fermeture RTH."""
        ts = pd.Timestamp("2025-01-06 20:00:00", tz="UTC")
        self.assertFalse(self.session_filter.is_rth_session(ts))


class TestCompressionDetector(unittest.TestCase):
    """Tests détecteur de compression."""
    
    def setUp(self):
        self.detector = CompressionDetector()
        
        # Créer DataFrame synthétique pour tests
        dates = pd.date_range("2025-01-01", periods=100, freq="15min")
        np.random.seed(42)
        
        # Données normales (volatilité moyenne)
        closes = np.random.normal(100, 2, 100).cumsum() + 100
        highs = closes + np.random.uniform(0, 1, 100)
        lows = closes - np.random.uniform(0, 1, 100)
        
        self.df_normal = pd.DataFrame({
            "open": closes,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": np.random.randint(100000, 500000, 100),
        }, index=dates)
        
        # Données comprimées (volatilité basse)
        closes_compressed = np.random.normal(100, 0.1, 100).cumsum() + 100
        highs_compressed = closes_compressed + np.random.uniform(0, 0.05, 100)
        lows_compressed = closes_compressed - np.random.uniform(0, 0.05, 100)
        
        self.df_compressed = pd.DataFrame({
            "open": closes_compressed,
            "high": highs_compressed,
            "low": lows_compressed,
            "close": closes_compressed,
            "volume": np.random.randint(100000, 500000, 100),
        }, index=dates)
    
    def test_compression_detection(self):
        """Détecte compression en données basses vol."""
        is_comp = self.detector.is_compression(self.df_compressed)
        self.assertTrue(is_comp)
    
    def test_normal_volatility_not_compression(self):
        """Données normales pas en compression."""
        is_comp = self.detector.is_compression(self.df_normal)
        self.assertFalse(is_comp)


class TestBreakoutSetupV1(unittest.TestCase):
    """Tests setup breakout v1."""
    
    def setUp(self):
        self.setup = BreakoutSetupV1()
        
        # Create test data
        dates = pd.date_range("2025-01-01", periods=30, freq="15min")
        base_price = 100
        
        # Données range-bound
        highs = [base_price + 1.0] * 30
        lows = [base_price - 1.0] * 30
        
        self.df_range = pd.DataFrame({
            "open": [base_price] * 30,
            "high": highs,
            "low": lows,
            "close": [base_price] * 30,
            "volume": [100000] * 30,
        }, index=dates)
    
    def test_long_breakout_detection(self):
        """Détecte long breakout."""
        df = self.df_range.copy()
        df.loc[df.index[-1], "close"] = 101.5  # Breakout haut
        
        signal = self.setup.get_breakout_signal(df)
        self.assertEqual(signal, "long")
    
    def test_short_breakout_detection(self):
        """Détecte short breakout."""
        df = self.df_range.copy()
        df.loc[df.index[-1], "close"] = 98.5  # Breakout bas
        
        signal = self.setup.get_breakout_signal(df)
        self.assertEqual(signal, "short")
    
    def test_no_breakout(self):
        """Pas de breakout si price dans range."""
        signal = self.setup.get_breakout_signal(self.df_range)
        self.assertIsNone(signal)


class TestPositionSizer(unittest.TestCase):
    """Tests position sizer."""
    
    def setUp(self):
        self.sizer = PositionSizer()
    
    def test_position_size_calculation(self):
        """Calcule taille position correctement."""
        account = 10000
        sl_distance = 25  # points
        
        size = self.sizer.calculate_position_size(
            account_balance=account,
            stop_loss_distance=sl_distance,
        )
        
        self.assertGreater(size, 0)
        self.assertEqual(type(size), int)
    
    def test_sl_placement_long(self):
        """SL placement pour long."""
        sl = self.sizer.get_stop_loss("long", range_high=101, range_low=99)
        self.assertEqual(sl, 99)
    
    def test_sl_placement_short(self):
        """SL placement pour short."""
        sl = self.sizer.get_stop_loss("short", range_high=101, range_low=99)
        self.assertEqual(sl, 101)
    
    def test_tp_calculation_long(self):
        """TP calculation pour long (3R)."""
        tp = self.sizer.get_take_profit(
            "long",
            entry_price=100,
            stop_loss=95,
            tp_ratio=3.0,
        )
        self.assertEqual(tp, 115)  # 100 + (3 * 5)
    
    def test_tp_calculation_short(self):
        """TP calculation pour short (3R)."""
        tp = self.sizer.get_take_profit(
            "short",
            entry_price=100,
            stop_loss=105,
            tp_ratio=3.0,
        )
        self.assertEqual(tp, 85)  # 100 - (3 * 5)
    
    def test_can_trade_yes(self):
        """Can take trade = oui."""
        can_trade, reason = self.sizer.can_take_trade(
            account_balance=10000,
            daily_loss=100,
            trades_today=0,
            current_position=False,
        )
        self.assertTrue(can_trade)
    
    def test_can_trade_max_daily_loss(self):
        """Can trade = non (max daily loss)."""
        can_trade, reason = self.sizer.can_take_trade(
            account_balance=10000,
            daily_loss=300,  # > 2.5%
            trades_today=0,
            current_position=False,
        )
        self.assertFalse(can_trade)


if __name__ == "__main__":
    unittest.main()
