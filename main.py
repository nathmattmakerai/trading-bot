"""
Orchestrateur principal: coordonne tous les modules.
"""

import pandas as pd
from typing import Optional, Tuple
import sys

# Imports
from config.rules_v1 import *
from data.futures_data_loader import FuturesDataLoader, MacroDataLoader, CalendarLoader
from engine.filters.macro_filter import MacroFilter, RiskRegime
from engine.filters.calendar_filter import CalendarFilter
from engine.filters.session_filter import SessionFilter
from engine.structure.compression_detector import CompressionDetector
from engine.setup.breakout_v1 import BreakoutSetupV1
from engine.risk.position_sizer import PositionSizer
from engine.backtest.engine_futures import BacktestEngine, TradeStatus
from broker.base_broker import SimulationBroker, Order


class TradingBot:
    """
    Orchestrateur du système de trading.
    
    Logique à chaque close 15m:
    1. Vérifier session autorisée
    2. Vérifier filtre calendrier
    3. Vérifier filtre macro
    4. Vérifier pas de position ouverte
    5. Vérifier max trades/jour
    6. Détecter compression
    7. Détecter breakout confirmé
    8. Calculer SL / TP
    9. Calculer taille position
    10. Exécuter trade
    11. Gérer jusqu'à TP / SL / fin session
    """
    
    def __init__(self, starting_balance: float = 10000.0):
        """Initialise le bot."""
        # Configuration PRD gelée
        self.rules = {
            "compression": COMPRESSION_CONFIG,
            "breakout": BREAKOUT_CONFIG,
            "macro": MACRO_FILTER_CONFIG,
            "calendar": CALENDAR_FILTER_CONFIG,
            "risk": RISK_CONFIG,
            "position": POSITION_CONFIG,
            "concurrent": CONCURRENT_RULES,
        }
        
        # Modules
        self.backtest_engine = BacktestEngine(starting_balance)
        self.broker = SimulationBroker()
        
        # Filtres
        self.macro_filter = MacroFilter(
            vix_risk_on_threshold=self.rules["macro"]["risk_on_vix"],
            vix_risk_off_threshold=self.rules["macro"]["risk_off_vix"],
        )
        self.calendar_filter = CalendarFilter()
        self.session_filter = SessionFilter()
        
        # Setup
        self.compression_detector = CompressionDetector(**self.rules["compression"])
        self.breakout_setup = BreakoutSetupV1(**self.rules["breakout"])
        
        # Risk management
        self.position_sizer = PositionSizer(**self.rules["risk"])
        
        # Data loaders
        self.futures_loader = FuturesDataLoader()
        self.macro_loader = MacroDataLoader()
        self.calendar_loader = CalendarLoader()
    
    def check_all_filters(
        self,
        timestamp: pd.Timestamp,
        vix: float,
        us10y_yield: float,
    ) -> Tuple[bool, str]:
        """
        Vérifie tous les filtres (session, calendrier, macro).
        
        Returns:
            Tuple (can_trade, reason)
        """
        # 1. Session filter
        if not self.session_filter.is_rth_session(timestamp):
            return False, "Outside RTH session"
        
        # 2. Calendrier filter
        if not self.calendar_filter.trading_allowed(timestamp):
            blackout_reason = self.calendar_filter.get_blackout_reason(timestamp)
            return False, f"Blackout: {blackout_reason}"
        
        # 3. Macro filter
        regime = self.macro_filter.get_risk_regime(vix, us10y_yield)
        filter_status = self.macro_filter.filter_status(regime)
        
        # Note: On retourne True ici parce que macro n'est pas un hard blocker
        # On l'utilisera pour filtrer les signaux
        return True, f"Macro regime: {regime.value}"
    
    def process_bar(
        self,
        timestamp: pd.Timestamp,
        instrument: str,
        df_instrument: pd.DataFrame,
        vix: float,
        us10y_yield: float,
    ) -> Optional[dict]:
        """
        Processe une bougie 15m pour générer/gérer trades.
        
        Returns:
            Dict avec détails trade exécutée ou None
        """
        # Update daily metrics
        self.backtest_engine.update_daily_metrics(timestamp)
        
        # Check all filters
        can_trade, filter_reason = self.check_all_filters(timestamp, vix, us10y_yield)
        
        if not can_trade:
            return None
        
        # Check one-at-a-time rule
        if self.backtest_engine.open_position:
            # Manage existing trade
            return self._manage_open_position(timestamp, df_instrument)
        
        # Check risk rules
        daily_loss = -self.backtest_engine.daily_pnl if self.backtest_engine.daily_pnl < 0 else 0
        can_take_trade, risk_reason = self.position_sizer.can_take_trade(
            account_balance=self.backtest_engine.current_balance,
            daily_loss=daily_loss,
            trades_today=self.backtest_engine.trades_today,
            current_position=bool(self.backtest_engine.open_position),
        )
        
        if not can_take_trade:
            return None
        
        # Detect compression
        is_compression = self.compression_detector.is_compression(df_instrument)
        
        if not is_compression:
            return None
        
        # Detect breakout
        signal = self.breakout_setup.get_breakout_signal(df_instrument)
        
        if not signal:
            return None
        
        # Check macro compatibility
        regime = self.macro_filter.get_risk_regime(vix, us10y_yield)
        macro_compatible = self.macro_filter.should_trade(regime, signal)
        
        if not macro_compatible:
            return None
        
        # Get setup levels
        levels = self.breakout_setup.get_setup_levels(df_instrument)
        range_high = levels["range_high"]
        range_low = levels["range_low"]
        
        # Get SL and TP
        current_close = df_instrument["close"].iloc[-1]
        sl = self.position_sizer.get_stop_loss(signal, range_high, range_low)
        tp = self.position_sizer.get_take_profit(signal, current_close, sl)
        
        # Calculate position size
        sl_distance = abs(current_close - sl)
        size = self.position_sizer.calculate_position_size(
            account_balance=self.backtest_engine.current_balance,
            stop_loss_distance=sl_distance,
        )
        
        # Execute trade
        trade = self.backtest_engine.execute_trade(
            timestamp=timestamp,
            instrument=instrument,
            direction=signal,
            entry_price=current_close,
            stop_loss=sl,
            take_profit=tp,
            size=size,
        )
        
        return {
            "trade_id": trade.trade_id,
            "timestamp": timestamp,
            "instrument": instrument,
            "direction": signal,
            "entry_price": current_close,
            "stop_loss": sl,
            "take_profit": tp,
            "size": size,
        }
    
    def _manage_open_position(
        self,
        timestamp: pd.Timestamp,
        df_instrument: pd.DataFrame,
    ) -> Optional[dict]:
        """
        Manage position ouverte (TP/SL/session end).
        
        Returns:
            Dict avec exit details ou None
        """
        if not self.backtest_engine.open_position:
            return None
        
        trade = self.backtest_engine.open_position
        current_close = df_instrument["close"].iloc[-1]
        
        # Check TP
        if trade.direction == "long":
            if current_close >= trade.take_profit:
                return self._close_trade(current_close, timestamp, "tp")
            elif current_close <= trade.stop_loss:
                return self._close_trade(current_close, timestamp, "sl")
        else:  # short
            if current_close <= trade.take_profit:
                return self._close_trade(current_close, timestamp, "tp")
            elif current_close >= trade.stop_loss:
                return self._close_trade(current_close, timestamp, "sl")
        
        return None
    
    def _close_trade(
        self,
        exit_price: float,
        exit_timestamp: pd.Timestamp,
        reason: str,
    ) -> dict:
        """Ferme une trade."""
        trade = self.backtest_engine.close_trade(
            exit_price=exit_price,
            exit_timestamp=exit_timestamp,
            reason=reason,
        )
        
        return {
            "trade_id": trade.trade_id,
            "exit_timestamp": exit_timestamp,
            "exit_price": exit_price,
            "exit_reason": reason,
            "pnl": trade.pnl,
            "pnl_pct": trade.pnl_pct,
        }
    
    def backtest(
        self,
        instrument: str,
        start_date: str,
        end_date: str,
    ) -> dict:
        """
        Lance backtest complet.
        
        Args:
            instrument: 'NQ' ou 'ES'
            start_date: YYYY-MM-DD
            end_date: YYYY-MM-DD
        
        Returns:
            Statistiques backtest
        """
        print(f"Starting backtest {instrument} from {start_date} to {end_date}...")
        
        # Load données
        df_futures = self.futures_loader.fetch_futures_data(
            instrument, start_date, end_date, "15m"
        )
        macro_data = self.macro_loader.combine_macro_data(start_date, end_date)
        
        # Process chaque bougie 15m
        processed = 0
        for idx, row in df_futures.iterrows():
            # Get macro data pour ce jour
            trade_date = idx.date()
            macro_row = macro_data.loc[trade_date] if trade_date in macro_data.index else None
            
            if macro_row is None:
                continue
            
            vix = macro_row["vix"]
            us10y = macro_row["us10y_yield"]
            
            # Process bar
            df_to_now = df_futures.iloc[:processed+1]
            self.process_bar(idx, instrument, df_to_now, vix, us10y)
            
            processed += 1
        
        # Close any open position at end
        if self.backtest_engine.open_position:
            last_price = df_futures["close"].iloc[-1]
            last_timestamp = df_futures.index[-1]
            self.backtest_engine.close_trade(last_price, last_timestamp, "session_end")
        
        # Get stats
        stats = self.backtest_engine.get_statistics()
        print(f"Backtest complete. Total trades: {stats.get('num_trades', 0)}")
        
        return stats


if __name__ == "__main__":
    print("Trading Bot Initialized")
    print(f"PRD Version: {VERSION}")
    print(f"Locked: {LOCKED}")
