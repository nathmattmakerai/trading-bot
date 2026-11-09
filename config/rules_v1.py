"""
PRD v1 - VERSION GELÉE
Configuration officielle du système de trading algorithmique futures intraday.
Toute déviation = défilement/fund failure.
"""

from config.base_config import BaseConfig
from typing import Any, Dict

class RulesV1(BaseConfig):
    # ===== INSTRUMENTS & SESSIONS =====
    VERSION = "v1_FROZEN"
    LOCKED = True
    INSTRUMENTS = ["NQ", "ES"]
    BASE_TIMEFRAME = "15m"
    CONTEXT_TIMEFRAMES = ["1h", "4h"]
    MACRO_TIMEFRAME = "1d"

    # Sessions trading autorisées (8:00 AM - 3:00 PM ET)
    TRADING_SESSION_UTC_START = 12  # 8:00 AM ET
    TRADING_SESSION_UTC_END = 19    # 3:00 PM ET

    # ===== UNIVERS DE DONNÉES =====
    DATA_SOURCES = {
        "futures_prices": "CME",  # NQ/ES
        "vix": "Yahoo Finance / Bloomberg",
        "us10y_yield": "US Treasury / Federal Reserve",
        "calendar": "Investing.com / Economic Calendar",
    }

    # ===== SETUP v1: BREAKOUT COMPRESSION =====
    COMPRESSION_CONFIG = {
        "atr_period": 14,
        "atr_lookback": 50,
        "range_lookback": 20,
        "atr_ratio_threshold": 0.75,   # PRD: ATR(14) < 0.75 * ATR(50)
        "range_ratio_threshold": 1.5,  # PRD: Range(20) < 1.5 * ATR(14)
    }

    BREAKOUT_CONFIG = {
        "range_lookback": 20,
    }

    # ===== FILTRE MACRO =====
    MACRO_FILTER_CONFIG = {
        "risk_on_vix": 18,  # PRD: VIX < 18 = long autorisé
        "risk_off_vix": 22, # PRD: VIX > 22 = short only
        "yield_rules": {
            "stable_or_rising": "long_ok",
            "sharp_decline": "short_only_or_no_trade",
        },
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

    # ===== RISK MANAGEMENT =====
    RISK_CONFIG = {
        "risk_per_trade": 0.0075,  # 0.75% (PRD)
        "max_daily_loss": 0.025,   # 2.5% (PRD)
        "max_trades_per_day": 2,   # 2 (PRD)
    }

    # ===== PRISE DE POSITION =====
    POSITION_CONFIG = {
        "stop_loss_placement": "opposite_side_of_range",
        "take_profit_ratio": 3.0,  # 3R (PRD)
        "trailing_stop": False,
        "breakeven": True,
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

    # ===== KPI CIBLES (STABILITÉ LONG TERME) =====
    TARGET_KPI = {
        "max_drawdown_pct": 3.5,
        "target_monthly_return_pct": 5.0,
        "minimum_track_record_months": 6,
    }

    # ===== RÈGLES ANTI-ÉGO (PROTECTION) =====
    FROZEN_RULES = """
❌ PAS d'ajout de setup avant 50+ trades backtestés
❌ PAS de "juste un petit trailing"
❌ PAS d'optimisation paramètre par paramètre
❌ PAS de live sans backtest stable

Chaque exception tue un futur fund manager.
"""

# Instance for backward compatibility and easy import
rules_v1 = RulesV1()

# Backward compatibility with old imports (direct access to variables)
VERSION = rules_v1.VERSION
LOCKED = rules_v1.LOCKED
INSTRUMENTS = rules_v1.INSTRUMENTS
BASE_TIMEFRAME = rules_v1.BASE_TIMEFRAME
CONTEXT_TIMEFRAMES = rules_v1.CONTEXT_TIMEFRAMES
MACRO_TIMEFRAME = rules_v1.MACRO_TIMEFRAME
DATA_SOURCES = rules_v1.DATA_SOURCES
COMPRESSION_CONFIG = rules_v1.COMPRESSION_CONFIG
BREAKOUT_CONFIG = rules_v1.BREAKOUT_CONFIG
MACRO_FILTER_CONFIG = rules_v1.MACRO_FILTER_CONFIG
CALENDAR_FILTER_CONFIG = rules_v1.CALENDAR_FILTER_CONFIG
RISK_CONFIG = rules_v1.RISK_CONFIG
POSITION_CONFIG = rules_v1.POSITION_CONFIG
SESSION_CONFIG = rules_v1.SESSION_CONFIG
CONCURRENT_RULES = rules_v1.CONCURRENT_RULES
TARGET_KPI = rules_v1.TARGET_KPI
FROZEN_RULES = rules_v1.FROZEN_RULES

# vv1_FROZEN for the web interface
vv1_FROZEN = rules_v1.to_dict()
