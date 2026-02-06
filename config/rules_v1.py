"""
PRD v1 - VERSION GELÉE
Configuration officielle du système de trading algorithmique futures intraday.
Toute déviation = défilement/fund failure.
"""

# ===== INSTRUMENTS & SESSIONS =====
INSTRUMENTS = ["NQ", "ES"]
BASE_TIMEFRAME = "15m"  # 15 minutes uniquement
CONTEXT_TIMEFRAMES = ["1h", "4h"]  # H1 / H4
MACRO_TIMEFRAME = "1d"  # Daily

# Sessions trading autorisées (RTH US uniquement)
TRADING_SESSION_UTC_START = 13  # 8:00 AM EST
TRADING_SESSION_UTC_END = 20  # 3:00 PM EST (fermeture RTH)

# ===== UNIVERS DE DONNÉES =====
DATA_SOURCES = {
    "futures_prices": "CME",  # NQ/ES
    "vix": "Yahoo Finance / Bloomberg",
    "us10y_yield": "US Treasury / Federal Reserve",
    "calendar": "Investing.com / Economic Calendar",
}

# ===== SETUP v1: BREAKOUT COMPRESSION =====
# Détection compression (ATR-based, plus robuste que BB)
COMPRESSION_CONFIG = {
    "atr_period": 14,
    "atr_lookback": 50,
    "range_lookback": 20,
    "atr_ratio_threshold": 0.75,  # ATR(14) < 0.75 * ATR(50)
    "range_ratio_threshold": 1.5,  # Range < 1.5 * ATR(14)
}

# Breakout confirmé: close > high range OU close < low range
BREAKOUT_CONFIG = {
    "range_lookback": 20,
}

# ===== FILTRE MACRO (OBLIGATOIRE) =====
MACRO_FILTER_CONFIG = {
    "risk_on_vix": 18,  # VIX < 18 = long autorisé
    "risk_off_vix": 22,  # VIX > 22 = short only ou no trade
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
    "blackout_buffer_days": 1,  # Veille + lendemain d'événements majeurs
}

# ===== RISK MANAGEMENT =====
RISK_CONFIG = {
    "risk_per_trade": 0.0075,  # 0.75%
    "max_daily_loss": 0.025,  # 2.5%
    "max_trades_per_day": 2,
}

# ===== PRISE DE POSITION =====
POSITION_CONFIG = {
    "stop_loss_placement": "opposite_side_of_range",
    "take_profit_ratio": 3.0,  # 3R
    "trailing_stop": False,  # NO trailing
    "breakeven": False,  # NO BE logic
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
    "max_concurrent_positions": 1,  # Une seule position ouverte
    "priority_instrument": "NQ",  # NQ en risk-on
    "fallback_instrument": "ES",  # ES seulement si NQ non tradable
}

# ===== KPI CIBLES (STABILITÉ LONG TERME) =====
TARGET_KPI = {
    "max_drawdown_pct": 3.5,  # DD < 3.5%
    "target_monthly_return_pct": 5.0,  # ≥ 5% mensuel moyen
    "minimum_track_record_months": 6,  # Stabilité sur ≥ 6 mois
}

# ===== RÈGLES ANTI-ÉGO (PROTECTION) =====
FROZEN_RULES = """
❌ PAS d'ajout de setup avant 50+ trades backtestés
❌ PAS de "juste un petit trailing"
❌ PAS d'optimisation paramètre par paramètre
❌ PAS de live sans backtest stable

Chaque exception tue un futur fund manager.
"""

# Version gelée - DO NOT TOUCH
VERSION = "v1_FROZEN"
LOCKED = True

# ===== EXPORT FOR INTERFACE =====
# Complete frozen configuration for web interface and documentation
vv1_FROZEN = {
    "VERSION": "v1_FROZEN",
    "LOCKED": True,
    "INSTRUMENTS": INSTRUMENTS,
    "BASE_TIMEFRAME": BASE_TIMEFRAME,
    "CONTEXT_TIMEFRAMES": CONTEXT_TIMEFRAMES,
    "MACRO_TIMEFRAME": MACRO_TIMEFRAME,
    "DATA_SOURCES": DATA_SOURCES,
    "COMPRESSION_CONFIG": COMPRESSION_CONFIG,
    "BREAKOUT_CONFIG": BREAKOUT_CONFIG,
    "RISK_CONFIG": RISK_CONFIG,
    "MACRO_FILTER_CONFIG": MACRO_FILTER_CONFIG,
    "CALENDAR_FILTER_CONFIG": CALENDAR_FILTER_CONFIG,
    "POSITION_CONFIG": POSITION_CONFIG,
    "SESSION_CONFIG": SESSION_CONFIG,
}
