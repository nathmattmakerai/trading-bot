"""
Paramètres contrats futures CME (NQ, ES).

Source: CME Group official specs
Last updated: 6 février 2026
"""

# ===== NASDAQ 100 MICRO FUTURES (MNQ) =====
NQ_SPEC = {
    "symbol": "NQ",
    "contract_name": "E-mini NASDAQ 100 Futures",
    "micro_contract": "Micro E-mini NASDAQ (MNQ)",
    
    # Specs
    "notional_value": 100 * 5080,  # ~$508,000 per contract (approx @ 5080)
    "point_value": 100,  # 1 point = $100
    "tick_size": 0.25,  # 1 tick = 0.25 points
    "tick_value": 25.0,  # 1 tick = $25
    
    # Micro version
    "micro_notional_value": 100 * 5080 / 10,  # ~$50,800
    "micro_tick_value": 2.5,  # 1 tick = $2.50 (MNQ)
    
    # Trading hours (CME Chicago)
    "rth_start_cst": "09:30",  # 9:30 AM CST
    "rth_end_cst": "16:00",    # 4:00 PM CST
    "pre_market_start": "08:00",
    "post_market_end": "17:00",
    
    # RTH in UTC
    "rth_start_utc": 15,  # 3:30 PM UTC (winter) or 2:30 PM (summer)
    "rth_end_utc": 22,    # 10:00 PM UTC (winter)
    
    # Rollover
    "rollover_days": [15, 16, 17],  # 3rd Fri monthly
    "contract_months": [3, 6, 9, 12],  # Mar, Jun, Sep, Dec
    
    # Liquidity
    "most_liquid_month": "Nearest",
    "typical_volume": 5_000_000,  # contracts daily
    
    # Commissions (Rithmic/TopstepX typical)
    "commission_round_trip": 2.50,  # dollars per trade (entry+exit)
    "slippage_typical": 0.5,  # ticks (1 tick = $25)
}

# ===== S&P 500 E-MINI FUTURES (ES) =====
ES_SPEC = {
    "symbol": "ES",
    "contract_name": "E-mini S&P 500 Futures",
    "micro_contract": "Micro E-mini S&P 500 (MES)",
    
    # Specs
    "notional_value": 50 * 5200,  # ~$260,000 per contract (approx @ 5200)
    "point_value": 50,  # 1 point = $50
    "tick_size": 0.25,  # 1 tick = 0.25 points
    "tick_value": 12.5,  # 1 tick = $12.50
    
    # Micro version
    "micro_notional_value": 50 * 5200 / 10,  # ~$26,000
    "micro_tick_value": 1.25,  # 1 tick = $1.25 (MES)
    
    # Trading hours (CME Chicago)
    "rth_start_cst": "09:30",  # 9:30 AM CST
    "rth_end_cst": "16:00",    # 4:00 PM CST
    "pre_market_start": "08:00",
    "post_market_end": "17:00",
    
    # RTH in UTC
    "rth_start_utc": 15,  # 3:30 PM UTC (winter)
    "rth_end_utc": 22,    # 10:00 PM UTC (winter)
    
    # Rollover
    "rollover_days": [15, 16, 17],  # 3rd Fri monthly
    "contract_months": [3, 6, 9, 12],  # Mar, Jun, Sep, Dec
    
    # Liquidity
    "most_liquid_month": "Nearest",
    "typical_volume": 8_000_000,  # contracts daily
    
    # Commissions
    "commission_round_trip": 2.00,  # dollars per trade
    "slippage_typical": 0.5,  # ticks (1 tick = $12.50)
}

# ===== GENERAL PARAMS =====
CME_SPECS = {
    "NQ": NQ_SPEC,
    "ES": ES_SPEC,
}

# RTH Session (US Eastern Time)
RTH_SESSION = {
    "name": "US Stock Market Hours (RTH)",
    "start_et": "08:00",  # 8:00 AM ET
    "end_et": "15:00",    # 3:00 PM ET (market close)
    
    # In UTC (varies by daylight saving)
    "start_utc_winter": 13,  # 1:00 PM UTC = 8:00 AM ET (EST)
    "end_utc_winter": 20,    # 8:00 PM UTC = 3:00 PM ET (EST)
    
    "start_utc_summer": 12,  # 12:00 PM UTC = 8:00 AM ET (EDT)
    "end_utc_summer": 19,    # 7:00 PM UTC = 3:00 PM ET (EDT)
}

# Pre-market and post-market
EXTENDED_SESSION = {
    "pre_market_start_et": "07:00",  # 7:00 AM ET
    "pre_market_end_et": "09:30",    # 9:30 AM ET (RTH open)
    
    "post_market_start_et": "15:00",  # 3:00 PM ET (RTH close)
    "post_market_end_et": "20:00",    # 8:00 PM ET
}

# Risk calculation helpers
def calculate_position_size(
    account: float,
    risk_pct: float,
    entry: float,
    stop_loss: float,
    instrument: str = "NQ",
) -> int:
    """
    Calcule position size pour futures.
    
    Args:
        account: Account balance
        risk_pct: Risk percentage (e.g., 0.75 for 0.75%)
        entry: Entry price
        stop_loss: Stop loss price
        instrument: 'NQ' or 'ES'
    
    Returns:
        Number of contracts (whole)
    """
    spec = CME_SPECS[instrument]
    tick_value = spec["tick_value"]
    
    risk_dollars = account * (risk_pct / 100)
    sl_distance = abs(entry - stop_loss)
    sl_dollars = sl_distance * tick_value
    
    size = risk_dollars / sl_dollars
    return int(size)


def calculate_risk_reward(
    entry: float,
    stop_loss: float,
    take_profit: float,
    size: int,
    instrument: str = "NQ",
) -> dict:
    """
    Calcule risk/reward pour trade.
    
    Args:
        entry: Entry price
        stop_loss: SL price
        take_profit: TP price
        size: Number of contracts
        instrument: 'NQ' or 'ES'
    
    Returns:
        Dict avec risk/reward metrics
    """
    spec = CME_SPECS[instrument]
    tick_value = spec["tick_value"]
    
    sl_distance = abs(entry - stop_loss)
    tp_distance = abs(entry - take_profit)
    
    risk_dollars = size * sl_distance * tick_value
    reward_dollars = size * tp_distance * tick_value
    ratio = reward_dollars / risk_dollars if risk_dollars > 0 else 0
    
    return {
        "sl_distance_points": sl_distance,
        "tp_distance_points": tp_distance,
        "risk_dollars": risk_dollars,
        "reward_dollars": reward_dollars,
        "ratio": ratio,
        "commission": spec["commission_round_trip"],
        "est_slippage": sl_distance * spec["slippage_typical"],
    }
