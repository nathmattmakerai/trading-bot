"""
Orchestrateur principal: coordonne tous les modules.
"""

import pandas as pd
from typing import Optional, Tuple
import sys
import logging

# Imports
from engine.backtest.engine_futures import BacktestEngine
from broker.base_broker import SimulationBroker
from engine.filters.macro_filter import MacroFilter
from engine.filters.calendar_filter import CalendarFilter
from engine.filters.session_filter import SessionFilter
from engine.structure.compression_detector import CompressionDetector
from engine.setup.breakout_v1 import BreakoutSetupV1
from engine.risk.position_sizer import PositionSizer
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
from config.config_manager import ConfigManager
# Import our enhanced sentiment analyzer
try:
    from data.sentiment_analyzer import get_market_sentiment
except ImportError:
    # Fallback if sentiment analyzer not available
    def get_market_sentiment(tickers=None):
        return {}
from engine.risk.equity_guard import EquityGuard
from data.futures_data_loader import FuturesDataLoader, MacroDataLoader
from data.calendar_loader import CalendarLoader
from engine.learning.error_analyzer import ErrorAnalyzer
from data.crawler import FinancialDataCrawler

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
        
        

    def get_market_sentiment(self, tickers=None):
        """
        Get market sentiment for specified tickers.

        Args:
            tickers: List of tickers to analyze. If None, uses default list.

        Returns:
            Dictionary with sentiment scores for each ticker
        """
        try:
            return get_market_sentiment(tickers)
        except Exception as e:
            print(f"Error getting market sentiment: {e}")
            # Return basic default sentiment data
            return {
                'NQ': {'sentiment': 'Neutral', 'score': 0.0, 'confidence': 0.5},
                'ES': {'sentiment': 'Neutral', 'score': 0.0, 'confidence': 0.5},
                'BTC': {'sentiment': 'Neutral', 'score': 0.0, 'confidence': 0.5}
            }

    def adaptive_strategy_selection(self, market_conditions):
        """
        Select the most appropriate trading strategy based on current market conditions.

        Args:
            market_conditions: Dictionary containing market indicators

        Returns:
            String representing the selected strategy
        """
        # Analyze market conditions
        sentiment_score = market_conditions.get('sentiment_score', 0)
        volatility = market_conditions.get('volatility', 0)
        trend = market_conditions.get('trend', 'neutral')

        # Strategy selection logic
        if sentiment_score > 0.5 and volatility < 0.3:
            return "aggressive_bullish"
        elif sentiment_score < -0.5 and volatility < 0.3:
            return "aggressive_bearish"
        elif volatility > 0.5:
            return "adaptive_volatility"
        elif trend == 'bullish':
            return "conservative_bullish"
        elif trend == 'bearish':
            return "conservative_bearish"
        else:
            return "neutral_adaptive"

        # Adjust learning rate based on market stability
        if performance_metrics.get('sharpe_ratio', 0) > 1.0:
            self.learning_rate = min(0.5, self.learning_rate * 1.1)
        else:
            self.learning_rate = max(0.01, self.learning_rate * 0.9)

    def run_backtest(self, instrument: str = "NQ", start_date: str = "2023-01-01",
                    end_date: str = "2023-12-31", strategy_config: dict = None) -> Dict:
        """
        Run a backtest simulation for the specified instrument.

        Args:
            instrument: Trading instrument (default: NQ)
            start_date: Start date for backtest
            end_date: End date for backtest
            strategy_config: Strategy configuration

        Returns:
            Dictionary with backtest results and statistics
        """
        try:
            logger.info(f"Starting backtest for {instrument} from {start_date} to {end_date}")

            # Initialize components
            if not self.bot:
                self.init_bot()

            # Load data using the data loader
            data_loader = FuturesDataLoader()
            macro_loader = MacroDataLoader()
            calendar_loader = CalendarLoader()

            # Load historical data
            df = data_loader.load_historical_data(instrument, start_date, end_date)
            if df is None or df.empty:
                raise ValueError(f"No data found for {instrument} from {start_date} to {end_date}")

            # Load macroeconomic data
            macro_df = macro_loader.load_macro_data(start_date, end_date)

            # Load calendar data
            calendar_df = calendar_loader.load_calendar_data(start_date, end_date)

            # Initialize broker and backtest engine
            broker = SimulationBroker(account_balance=10000.0)
            backtest_engine = BacktestEngine(broker)

            # Run simulation
            stats = backtest_engine.run_simulation(df, macro_df, calendar_df, instrument)

            # Get final statistics from the backtest engine
            final_stats = backtest_engine.get_statistics()

            logger.info(f"Backtest completed for {instrument}")

            return {
                'status': 'success',
                'instrument': instrument,
                'start_date': start_date,
                'end_date': end_date,
                'statistics': final_stats,
                'raw_data': stats
            }

        except Exception as e:
            logger.error(f"Error in backtest: {e}", exc_info=True)
            return {
                'status': 'error',
                'instrument': instrument,
                'error': str(e),
                'message': 'Backtest failed due to an error'
            }

    def collect_financial_data(self):
        """
        Collect financial data for analysis.

        Returns:
            Dictionary with collected data
        """
        # In a real implementation, this would connect to web sources or APIs
        # For now, we'll return mock data

        try:
            # Mock data collection - in production this would be actual web scraping or API calls
            data = {
                'price_data': [
                    {'ticker': 'NQ', 'price': 18000.0, 'volume': 1000000},
                    {'ticker': 'ES', 'price': 4500.0, 'volume': 500000},
                    {'ticker': 'BTC', 'price': 65000.0, 'volume': 2000000}
                ],
                'sentiment_data': [
                    {'ticker': 'NQ', 'sentiment_score': 0.7, 'confidence': 0.8},
                    {'ticker': 'ES', 'sentiment_score': -0.3, 'confidence': 0.6},
                    {'ticker': 'BTC', 'sentiment_score': 0.9, 'confidence': 0.9}
                ]
            }
            return data
        except Exception as e:
            print(f"Error collecting financial data: {e}")
            return {}

    def update_data_sources(self):
        """
        Update data sources and database with new information.
        """
        try:
            # In a real implementation, this would update the database with new data
            print("🔄 Updating data sources...")

            # This is where we would integrate with our data collector
            financial_data = self.collect_financial_data()

            # Process and store data
            if 'sentiment_data' in financial_data:
                for sentiment in financial_data['sentiment_data']:
                    print(f"📊 Stored sentiment for {sentiment['ticker']}: {sentiment['sentiment_score']}")

            print(" Data sources updated successfully")
        except Exception as e:
            print(f"Error updating data sources: {e}")

    def crawl_and_update_data(self, period: str = "2y"):
        """
        Crawl financial data and update the system with new information.

        Args:
            period: Time period for data collection

        Returns:
            Dictionary with summary of crawled data
        """
        try:
            print("🔄 Crawling financial data...")

            # Initialize crawler
            crawler = FinancialDataCrawler()

            # Crawl all data types
            data = crawler.crawl_all_data(period=period)

            # Save to file for persistence
            crawler.save_data(data, f'crawled_data_{period}.json')

            print("✅ Data crawling completed successfully")
            print(f"   Stocks: {len(data.get('stocks', {}))}")
            print(f"   Cryptos: {len(data.get('crypto', {}))}")
            print(f"   Futures: {len(data.get('futures', {}))}")
            print(f"   Sentiment data: {len(data.get('sentiment', {}))}")

            return data

        except Exception as e:
            print(f"❌ Error in crawling data: {e}")
            return {}

