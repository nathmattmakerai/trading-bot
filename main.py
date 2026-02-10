"""
Orchestrateur principal: coordonne tous les modules.
"""

import pandas as pd
from typing import Optional, Tuple
import sys

# Imports
from engine.backtest.engine_futures import BacktestEngine
from broker.base_broker import SimulationBroker
from engine.filters.macro_filter import MacroFilter
from engine.filters.calendar_filter import CalendarFilter
from engine.filters.session_filter import SessionFilter
from engine.structure.compression_detector import CompressionDetector
from engine.setup.breakout_v1 import BreakoutSetupV1
from engine.risk.position_sizer import PositionSizer
from engine.risk.equity_guard import EquityGuard
from data.futures_data_loader import FuturesDataLoader, MacroDataLoader
from data.calendar_loader import CalendarLoader
from engine.learning.error_analyzer import ErrorAnalyzer

# Configuration par défaut
from config.rules_v1 import (
    COMPRESSION_CONFIG,
    BREAKOUT_CONFIG,
    MACRO_FILTER_CONFIG,
    CALENDAR_FILTER_CONFIG,
    RISK_CONFIG,
    POSITION_CONFIG,
    CONCURRENT_RULES,
)


class TradingBot:
    """
    Bot de trading principal.
    
    Orchestre:
    1. Chargement données
    2. Filtres (Macro, Calendrier, Session)
    3. Détection Setup (Compression + Breakout)
    4. Risk Management (Position Sizing)
    5. Exécution (Simulée)
    6. Gestion positions
    
    Cycle de vie:
    1. Charger données historiques
    2. Pour chaque barre 15m:
    3.   Mettre à jour indicateurs
    4.   Vérifier filtres
    5.   Si setup -> vérifier risk -> exécuter
    6.   Gérer positions ouvertes (TP/SL)
    7.   Journaliser
    8. Fin de journée -> Rapport
    9. Fin de backtest -> Stats
    
    Règles strictes (Hardcoded):
    10. Pas de trade si High Impact News (sauf si position deja ouverte -> BE)
    11. Gérer jusqu'à TP / SL / fin session
    """
    
    def __init__(self, starting_balance: float = 10000.0, custom_risk_config: dict = None, custom_contract_config: dict = None):
        """
        Initialise le bot.
        """
        # Configuration PRD gelée comme base
        self.rules = {
            "compression": COMPRESSION_CONFIG,
            "breakout": BREAKOUT_CONFIG,
            "macro": MACRO_FILTER_CONFIG,
            "calendar": CALENDAR_FILTER_CONFIG,
            "risk": RISK_CONFIG.copy(),
            "position": POSITION_CONFIG,
            "concurrent": CONCURRENT_RULES,
        }
        
        # Override risk config
        if custom_risk_config:
            for key, value in custom_risk_config.items():
                if key in self.rules["risk"]:
                    self.rules["risk"][key] = value
        
        # Configuration contrat intelligent
        # Si capital < $20,000, on force les Micros ($2/pt pour MNQ)
        # Sinon on reste sur E-mini ($20/pt pour NQ)
        self.tick_value = 20.0
        self.is_micro = False
        
        if starting_balance < 20000:
            self.tick_value = 2.0  # Micro MNQ/MES
            self.is_micro = True
            print(f"Capital < $20k: Auto-switching to Micro contracts ($2/pt)")
        
        if custom_contract_config and "tick_value" in custom_contract_config:
            self.tick_value = custom_contract_config["tick_value"]
        
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
        self.equity_guard = EquityGuard()  # Protection adaptative
        self.error_analyzer = ErrorAnalyzer() # Système d'apprentissage
        self.error_analyzer.load_memory()      # Charger l'expérience passée
        
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
        
        # 1. Manage open positions FIRST (Exit logic is priority)
        if self.backtest_engine.open_position:
            return self._manage_open_position(timestamp, df_instrument)

        # 1. Check all standard filters (permissive version)
        can_trade, filter_reason = self.check_all_filters(timestamp, vix, us10y_yield)
        
        # 2. Detect signal
        signal = self.breakout_setup.get_breakout_signal(df_instrument)
        
        # 3. Check macro regime
        regime = self.macro_filter.get_risk_regime(vix, us10y_yield)
        macro_compatible = self.macro_filter.should_trade(regime, signal) if signal else True

        # Signal analysis for learning
        comp_metrics = self.compression_detector.get_compression_metrics(df_instrument)
        metadata = {
            "vix": vix,
            "us10y_yield": us10y_yield,
            "atr_ratio": comp_metrics.get("atr_ratio", 0),
            "range_ratio": comp_metrics.get("range_ratio", 0),
        }

        # [SKIP LOGIC FOR DASHBOARD] Si on a un signal mais bloqué par filtres macro/session
        if signal and (not can_trade or not macro_compatible):
            levels = self.breakout_setup.get_setup_levels(df_instrument)
            current_close = df_instrument["close"].iloc[-1]
            sl = self.position_sizer.get_stop_loss(signal, levels["range_high"], levels["range_low"])
            tp = self.position_sizer.get_take_profit(signal, current_close, sl, tp_ratio=self.rules["position"]["take_profit_ratio"])
            
            metadata["filter_skipped"] = True
            metadata["avoid_reason"] = filter_reason if not can_trade else "Macro Context Risk"

            self.backtest_engine.execute_trade(
                timestamp=timestamp, instrument=instrument, direction=signal,
                entry_price=current_close, stop_loss=sl, take_profit=tp,
                size=1, is_virtual=True, metadata=metadata,
                multiplier=self.tick_value, commission_per_contract=0
            )
            return {"trade_id": "skipped", "is_virtual": True, "reason": metadata["avoid_reason"]}

        if not can_trade or not signal:
            return None
            
        # 4. LEARNER GUARD: Check if this condition has been toxic in the past
        should_avoid, avoid_reason = self.error_analyzer.should_avoid_trade(metadata)
        
        # Get setup levels
        levels = self.breakout_setup.get_setup_levels(df_instrument)
        range_high = levels["range_high"]
        range_low = levels["range_low"]
        
        # Pricing
        current_close = df_instrument["close"].iloc[-1]
        sl = self.position_sizer.get_stop_loss(signal, range_high, range_low)
        tp = self.position_sizer.get_take_profit(signal, current_close, sl)
        
        # Position sizing
        size = self.position_sizer.calculate_position_size(
            account_balance=self.backtest_engine.current_balance,
            stop_loss_distance=abs(current_close - sl),
            tick_value=self.tick_value,
        )
        
        # 5. EQUITY GUARD & LEARNER DECISION
        is_virtual = False
        if should_avoid:
            is_virtual = True
            metadata["learner_skipped"] = True
            metadata["avoid_reason"] = avoid_reason
        elif not self.equity_guard.can_trade():
            is_virtual = True
            metadata["equity_skipped"] = True

        if is_virtual:
            if size == 0: size = 1 
        
        # Execute Final Trade
        trade = self.backtest_engine.execute_trade(
            timestamp=timestamp,
            instrument=instrument,
            direction=signal,
            entry_price=current_close,
            stop_loss=sl,
            take_profit=tp,
            size=size,
            is_virtual=is_virtual,
            metadata=metadata,
            multiplier=self.tick_value,
            commission_per_contract=2.50,
        )
        
        return {
            "trade_id": trade.trade_id,
            "timestamp": timestamp,
            "instrument": instrument,
            "direction": signal,
            "is_virtual": is_virtual,
            "is_learner_skipped": should_avoid
        }
    
    def _manage_open_position(
        self,
        timestamp: pd.Timestamp,
        df_instrument: pd.DataFrame,
    ) -> Optional[dict]:
        """
        Manage position ouverte (TP/SL/session end).
        Vérification réaliste utilisant High/Low pour TP/SL.
        """
        if not self.backtest_engine.open_position:
            return None
        
        trade = self.backtest_engine.open_position
        bar = df_instrument.iloc[-1]
        high = bar["high"]
        low = bar["low"]
        close = bar["close"]
        
        if trade.direction == "long":
            # [Pessimiste] Priorité au SL si les deux sont touchés dans la même barre
            if low <= trade.stop_loss:
                return self._close_trade(trade.stop_loss, timestamp, "sl")
            elif high >= trade.take_profit:
                return self._close_trade(trade.take_profit, timestamp, "tp")
                
            # [NOUVEAU] Logique Breakeven
            # Si on a fait 60% du chemin vers le TP, on sécurise au break even
            half_tp_dist = (trade.take_profit - trade.entry_price) * 0.6
            if high >= (trade.entry_price + half_tp_dist):
                if trade.stop_loss < trade.entry_price:
                    trade.stop_loss = trade.entry_price
        else:  # short
            if high >= trade.stop_loss:
                return self._close_trade(trade.stop_loss, timestamp, "sl")
            elif low <= trade.take_profit:
                return self._close_trade(trade.take_profit, timestamp, "tp")
                
            # [NOUVEAU] Logique Breakeven
            half_tp_dist = (trade.entry_price - trade.take_profit) * 0.6
            if low <= (trade.entry_price - half_tp_dist):
                if trade.stop_loss > trade.entry_price:
                    trade.stop_loss = trade.entry_price
        
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
        
        # Update Equity Guard (adaptive protection)
        # Note: On utilise le PnL en % du compte pour la protection du capital
        guard_msg = self.equity_guard.update_after_trade(trade.pnl_pct_account)
        if guard_msg:
            print(f"[Equity Guard] {guard_msg}")
        
        return {
            "trade_id": trade.trade_id,
            "exit_timestamp": exit_timestamp,
            "exit_price": exit_price,
            "exit_reason": reason,
            "pnl": trade.pnl,
            "pnl_pct": trade.pnl_pct,
            "is_virtual": trade.is_virtual,
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
        
        # [NEW] LEARNING PHASE: Analyse errors to refine future decisions
        closed_trades_data = [
            {
                "pnl_pct_account": t.pnl_pct_account,
                "metadata": t.metadata
            }
            for t in self.backtest_engine.closed_trades
        ]
        
        if len(closed_trades_data) > 0:
            learning_report = self.error_analyzer.analyze_backtest_results(closed_trades_data)
            num_zones = learning_report.get('danger_zones_identified', 0)
            if num_zones > 0:
                self.error_analyzer.save_memory() # Persister l'apprentissage
                print(f"[Learning] Strategy self-corrected. Memory updated with {num_zones} danger zones.")
        
        return stats


if __name__ == "__main__":
    print("Trading Bot Initialized")
    print(f"PRD Version: {VERSION}")
    print(f"Locked: {LOCKED}")
