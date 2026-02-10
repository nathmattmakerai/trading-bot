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

# Sessions trading autorisées (Plus large : 7:00 AM - 4:00 PM EST)
TRADING_SESSION_UTC_START = 12  # 7:00 AM EST
TRADING_SESSION_UTC_END = 21  # 4:00 PM EST (clôture NYSE)

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
    "atr_ratio_threshold": 0.8,   # PRO : Ne trade que les vraies compressions
    "range_ratio_threshold": 2.5,  # PRO : Range resserré pour éviter les faux breakouts
}

# Breakout confirmé: close > high range OU close < low range
BREAKOUT_CONFIG = {
    "range_lookback": 20,
}

# ===== FILTRE MACRO (MOINS RESTRICTIF) =====
MACRO_FILTER_CONFIG = {
    "risk_on_vix": 25,  # VIX < 25 = long autorisé
    "risk_off_vix": 35,  # VIX > 35 = short only ou no trade
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
    "risk_per_trade": 0.02,   # 2% (Gestion professionnelle)
    "max_daily_loss": 0.06,   # 6.0% (Marge de manoeuvre)
    "max_trades_per_day": 10, # 10 trades (Liberté totale)
}

# ===== PRISE DE POSITION =====
POSITION_CONFIG = {
    "stop_loss_placement": "opposite_side_of_range",
    "take_profit_ratio": 2.5,  # 2.5R (Plus réaliste pour les futurs)
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
