"""
PRD v2 - NEXT GENERATION
Advanced configuration for the optimized trading bot.
"""

from config.base_config import BaseConfig
from typing import Any, Dict

class RulesV2(BaseConfig):
    VERSION = "v2_OPTIMIZED"
    LOCKED = False  # v2 is meant to be refined
    INSTRUMENTS = ["NQ", "ES"]
    BASE_TIMEFRAME = "15m"
    CONTEXT_TIMEFRAMES = ["1h", "4h"]
    MACRO_TIMEFRAME = "1d"

    # Extended trading hours (including some pre-market if needed, but sticking to RTH for now)
    TRADING_SESSION_UTC_START = 12
    TRADING_SESSION_UTC_END = 19

    DATA_SOURCES = {
        "futures_prices": "CME",
        "vix": "Yahoo Finance / Bloomberg",
        "us10y_yield": "US Treasury / Federal Reserve",
        "calendar": "Investing.com / Economic Calendar",
    }

    # ===== SETUP v2: ENHANCED COMPRESSION =====
    COMPRESSION_CONFIG = {
        "atr_period": 14,
        "atr_lookback": 50,
        "range_lookback": 20,
        "atr_ratio_threshold": 0.70,   # Tighter compression for v2
        "range_ratio_threshold": 1.2,  # Tighter range for v2
        "super_compression_mode": True, # New: Ultra-tight requirements
    }

    BREAKOUT_CONFIG = {
        "range_lookback": 20,
        "momentum_filter": True, # New: check for strong momentum on breakout
    }

    # ===== FILTRE MACRO (ADVANCED) =====
    MACRO_FILTER_CONFIG = {
        "risk_on_vix": 15,   # Tighter threshold
        "risk_off_vix": 25,  # More conservative
        "yield_rules": {
            "stable_or_rising": "long_ok",
            "sharp_decline": "short_only_or_no_trade",
        },
        "volatility_regime_scaling": True, # New: scaling risk based on VIX volatility
    }

    # ===== FILTRE CALENDRIER (BLACKOUT) =====
    CALENDAR_FILTER_CONFIG = {
        "blackout_events": [
            "FOMC",
            "CPI",
            "NFP",
            "Payrolls",
        ],
        "blackout_days": ["rollover_days"],
        "blackout_buffer_days": 1,
    }

    # ===== RISK MANAGEMENT (DYNAMIC) =====
    RISK_CONFIG = {
        "base_risk_per_trade": 0.0075,  # 0.75%
        "max_risk_per_trade": 0.015,    # Max 1.5% if winning streak is high
        "max_daily_loss": 0.025,        # 2.5%
        "max_trades_per_day": 3,        # Slightly more flexibility
        "dynamic_scaling": True,        # New: scale risk based on account equity
    }

    # ===== PRISE DE POSITION =====
    POSITION_CONFIG = {
        "stop_loss_placement": "opposite_side_of_range",
        "take_profit_ratio": 3.0,
        "trailing_stop": True,          # New: trailing stop enabled in v2
        "breakeven_trigger": 0.6,       # New: breakeven at 60% of TP
        "trailing_stop_activation": 1.5, # New: trail after 1.5R profit
    }

    # ===== SESSION TRADING =====
    SESSION_CONFIG = {
        "rth_open": "8:00 AM ET",
        "rth_close": "3:00 PM ET",
        "utc_start": TRADING_SESSION_UTC_START,
        "utc_end": TRADING_SESSION_UTC_END,
    }

    # ===== ONE-TRADE-AT-A-TIME RULE =====
    CONCURRENT_RULES = {
        "max_concurrent_positions": 1,
        "priority_instrument": "NQ",
        "fallback_instrument": "ES",
    }

    # ===== BACKTEST REALISM (NEW) =====
    BACKTEST_PARAMS = {
        "slippage_ticks": 1,      # New: Add 1 tick slippage per trade
        "commission_per_contract": 2.50, # New: Realistic CME commission
        "latency_ms": 100,        # New: Simulate 100ms execution latency
    }

    # ===== KPI CIBLES =====
    TARGET_KPI = {
        "max_drawdown_pct": 3.0,  # More aggressive drawdown target
        "target_monthly_return_pct": 7.0,
        "minimum_track_record_months": 6,
    }

# Instance for easy import
rules_v2 = RulesV2()

# Backward compatibility (if needed)
VERSION = rules_v2.VERSION
LOCKED = rules_v2.LOCKED
INSTRUMENTS = rules_v2.INSTRUMENTS
COMPRESSION_CONFIG = rules_v2.COMPRESSION_CONFIG
RISK_CONFIG = rules_v2.RISK_CONFIG
MACRO_FILTER_CONFIG = rules_v2.MACRO_FILTER_CONFIG
CALENDAR_FILTER_CONFIG = rules_v2.CALENDAR_FILTER_CONFIG
POSITION_CONFIG = rules_v2.POSITION_CONFIG
SESSION_CONFIG = rules_v2.SESSION_CONFIG
CONCURRENT_RULES = rules_v2.CONCURRENT_RULES
TARGET_KPI = rules_v2.TARGET_KPI
BACKTEST_PARAMS = rules_v2.BACKTEST_PARAMS

# Export for interface
vv2_FROZEN = rules_v2.to_dict()
