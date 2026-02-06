# DOCUMENTATION TECHNIQUE - PRD v1 FROZEN

## 📋 Vue d'ensemble

Le bot est un système de trading algorithmique futures basé sur un setup unique de breakout compression, avec filtrage macro et gestion du risque strict.

## 🏗️ Modules Principaux

### 1. Configuration (`config/rules_v1.py`)
**Statut**: GELÉ - Aucune modification

Contient tous les paramètres PRD v1 hard-codés:
- Timeframe et instruments
- Paramètres compression/breakout
- Risk management
- KPI cibles
- Règles anti-ego

### 2. Data Loaders (`data/`)

#### `futures_data_loader.py`
- `FuturesDataLoader`: Charge NQ/ES depuis Yahoo Finance
  - Méthode: `fetch_futures_data()` - 15m/1h/4h
  - Méthode: `resample_to_timeframe()` - Resample custom
  - Méthode: `verify_data_continuity()` - Check gaps/NaNs

#### `macro_data_loader.py`
- `MacroDataLoader`: Charge VIX et US10Y yield
  - Méthode: `fetch_vix()` - Récupère VIX
  - Méthode: `fetch_us10y_yield()` - Récupère US10Y
  - Méthode: `combine_macro_data()` - Combine les deux
- `EconomicCalendarLoader`: Calendrier économique

#### `calendar_loader.py`
- `CalendarLoader`: Événements et rollovers
  - Dates hard-codées 2025 (FOMC, NFP, CPI, rollover)
  - Méthode: `is_blackout_date()` - Vérifie blackout
  - Méthode: `get_blackout_reason()` - Détaille raison

### 3. Filtres (`engine/filters/`)

#### `macro_filter.py`
```python
MacroFilter:
  - get_risk_regime(vix, us10y_yield) -> RiskRegime
  - should_trade(regime, direction) -> bool
  - is_long_allowed() / is_short_allowed()
```

Régimes:
- **RISK_ON**: VIX < 18 & yields ↑ → Long OK
- **RISK_OFF**: VIX > 22 ou yields ↓ → Short only
- **NEUTRAL**: 18 < VIX < 22 → Sélectif

#### `calendar_filter.py`
```python
CalendarFilter:
  - is_blackout_date(timestamp) -> bool
  - get_blackout_reason() -> str
  - trading_allowed() -> bool
```

Blackout: FOMC, NFP, CPI, Rollover + buffer jours

#### `session_filter.py`
```python
SessionFilter:
  - is_rth_session(timestamp) -> bool
  - is_trading_allowed() -> bool
  - get_session_info() -> dict
```

RTH US uniquement: 8:00 AM - 3:00 PM ET (13:00 - 20:00 UTC)

### 4. Structure (`engine/structure/`)

#### `compression_detector.py`
```python
CompressionDetector:
  - is_compression(df) -> bool
  - get_compression_metrics() -> dict
```

Critères compression:
1. `ATR(14) < 0.75 × ATR(50)`
2. `Range(20) < 1.5 × ATR(14)`

Les deux doivent être true.

### 5. Setup (`engine/setup/`)

#### `breakout_v1.py`
```python
BreakoutSetupV1:
  - detect_long_breakout() -> bool
  - detect_short_breakout() -> bool
  - get_breakout_signal() -> 'long'|'short'|None
```

Logique:
- **Long**: `close > max(high[-20:])`
- **Short**: `close < min(low[-20:])`
- Confirmation par close (pas intrabar)

### 6. Risk Management (`engine/risk/`)

#### `position_sizer.py`
```python
PositionSizer:
  - calculate_position_size() -> int (whole contracts)
  - get_stop_loss() -> float
  - get_take_profit() -> float (3R fixe)
  - can_take_trade() -> (bool, reason)
```

Formule position sizing:
```
Risk_$ = account × 0.75%
SL_distance = abs(entry - SL)
Size = Risk_$ / (SL_distance × tick_value)
→ Round down to whole contracts
```

Règles:
- Max 0.75% risque/trade
- Max 2.5% drawdown daily
- Max 2 trades/jour
- One-at-a-time

### 7. Backtest (`engine/backtest/`)

#### `engine_futures.py`
```python
BacktestEngine:
  - execute_trade() -> Trade
  - close_trade() -> Trade
  - get_equity_curve() -> DataFrame
  - get_statistics() -> dict
```

Tracking complet:
- Trades ouvertes/fermées
- PnL par trade
- Equity curve dynamique
- Stats: win rate, DD max, etc.

### 8. Brokers (`broker/`)

#### `base_broker.py`
```python
BaseBroker (abstract):
  - submit_order()
  - cancel_order()
  - get_position()
  - close_position()

SimulationBroker:
  - Exécution immédiate au prix demandé

RithmicBroker (TopstepX):
  - Connexion API Rithmic
  - Placeholder à implémenter
```

### 9. Orchestrateur (`main.py`)

```python
TradingBot:
  - process_bar() - Processe chaque bougie 15m
  - check_all_filters() - Valide tous filtres
  - backtest() - Lance backtest complet
```

Logique par bougie:
```
1. Check session RTH
2. Check calendrier (pas blackout)
3. Check macro (regime compatible)
4. Check position (one-at-a-time)
5. Check risk rules (max DD, trades/jour)
6. Detect compression
7. Detect breakout
8. Gérer position existante (TP/SL/session end)
```

## 🔄 Flux d'Exécution Complet

### 1. Initialisation
```python
from main import TradingBot

bot = TradingBot(starting_balance=10000)
```

### 2. Backtest
```python
stats = bot.backtest(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31",
)
```

### 3. Données chargées
- Futures 15m (resample si nécessaire)
- Macro daily (VIX + US10Y)
- Calendrier blackout

### 4. Pour chaque bougie 15m
```
data_timestamp = 2024-01-05 09:30:00
data_ohlc = [open, high, low, close, volume]
macro = {vix: 15.5, us10y_yield: 4.25}

1. Session check:
   - 09:30 EST = 14:30 UTC = dans RTH ✓

2. Calendar check:
   - 2024-01-05 = pas blackout ✓

3. Macro check:
   - VIX 15.5 < 18 ✓ → RISK_ON
   - Yields stables ✓
   → Long peut être tradé

4. Position check:
   - Pas de position ouverte ✓

5. Risk check:
   - Trades today: 0 < 2 ✓
   - Daily loss: 0 < 2.5% ✓

6. Compression detect:
   - ATR(14) vs ATR(50) ✓
   - Range(20) vs ATR(14) ✓
   → Compression détectée

7. Breakout detect:
   - close 101.5 > max(range[-20:]) 101.0 ✓
   → Long signal

8. Macro compat:
   - Signal: long
   - Regime: RISK_ON
   → Compatible ✓

9. Levels:
   - Entry: 101.5
   - SL (range_low): 99.0
   - TP (3R): 101.5 + (3×2.5) = 109.0

10. Position size:
    - Risk_$ = 10000 × 0.75% = 75
    - SL_distance = 2.5 points
    - SL_$ = 2.5 × 20 = 50
    - Size = 75 / 50 = 1.5 → 1 contract

11. Execute:
    - Trade #1: Long 1 NQ @ 101.5, SL 99.0, TP 109.0

12. Management (prochaines bougies):
    - Checker si close >= 109.0 (TP) → Exit avec +pnl
    - Checker si close <= 99.0 (SL) → Exit avec -pnl
    - Fin de session (15:00 ET) → Exit au close
```

## 📊 Données & Formats

### DataFrame Standard
```
Index: DatetimeIndex (UTC)
Columns: [open, high, low, close, volume]
```

### Trade Object
```python
Trade:
  - trade_id: int
  - timestamp: pd.Timestamp
  - instrument: str ('NQ', 'ES')
  - direction: str ('long', 'short')
  - entry_price: float
  - stop_loss: float
  - take_profit: float
  - size: int (whole contracts)
  - exit_timestamp: pd.Timestamp
  - exit_price: float
  - exit_reason: str ('tp', 'sl', 'session_end')
  - pnl: float (dollars)
  - pnl_pct: float (%)
```

### Statistics Return
```python
{
    'starting_balance': float,
    'final_balance': float,
    'total_pnl': float,
    'total_return_pct': float,
    'num_trades': int,
    'num_wins': int,
    'num_losses': int,
    'win_rate': float,
    'avg_win': float,
    'avg_loss': float,
    'largest_win': float,
    'largest_loss': float,
    'max_drawdown_pct': float,
}
```

## ⚙️ Paramètres Figés

| Paramètre | Valeur | Notes |
|-----------|--------|-------|
| Timeframe | 15m | Uniquement |
| Context TF | 1h, 4h | Pour contexte seulement |
| Macro TF | 1d | VIX + US10Y |
| ATR(short) | 14 | Compression |
| ATR(long) | 50 | Compression |
| ATR ratio | 0.75 | Seuil compression |
| Range lookback | 20 | Bougies pour range |
| Range ratio | 1.5 | vs ATR(14) |
| TP ratio | 3.0 | 3R fixe (no trailing) |
| Risk/trade | 0.75% | Capital |
| Max daily loss | 2.5% | Capital |
| Max trades/day | 2 | Hard limit |
| VIX risk-on | 18 | Seuil bas |
| VIX risk-off | 22 | Seuil haut |
| RTH start | 13:00 UTC | 8:00 AM ET |
| RTH end | 20:00 UTC | 3:00 PM ET |
| Calendar buffer | 1 day | Avant/après événement |

## 🧪 Tests

Exécuter la suite complète:
```bash
python -m pytest tests/validation_suite.py -v
```

Tests couvrent:
- MacroFilter (régimes, long/short allowed)
- CalendarFilter (blackout, buffer)
- SessionFilter (RTH detection)
- CompressionDetector (ATR/range logic)
- BreakoutSetupV1 (long/short signals)
- PositionSizer (sizing, SL, TP, risk rules)

## 🐛 Debugging

### Trace une trade complète
```python
# Récupérer liste trades
for trade in bot.backtest_engine.closed_trades:
    print(f"Trade #{trade.trade_id}")
    print(f"  Direction: {trade.direction}")
    print(f"  Entry: {trade.entry_price} @ {trade.timestamp}")
    print(f"  SL: {trade.stop_loss}, TP: {trade.take_profit}")
    print(f"  Exit: {trade.exit_price} @ {trade.exit_timestamp}")
    print(f"  Reason: {trade.exit_reason}")
    print(f"  PnL: ${trade.pnl:.2f} ({trade.pnl_pct:.1f}%)")
```

### Trace compression detection
```python
from engine.structure.compression_detector import CompressionDetector

detector = CompressionDetector()
metrics = detector.get_compression_metrics(df)
print(f"ATR(14): {metrics['atr_14']:.2f}")
print(f"ATR(50): {metrics['atr_50']:.2f}")
print(f"Ratio: {metrics['atr_ratio']:.2f} (threshold: {metrics['atr_threshold']})")
print(f"Compressed: {metrics['is_compression']}")
```

### Trace filtres
```python
# Macro
regime = bot.macro_filter.get_risk_regime(vix, us10y)
print(f"Regime: {regime.value}")
print(f"Long allowed: {bot.macro_filter.is_long_allowed(regime)}")

# Calendar
blackout = bot.calendar_filter.is_blackout_date(timestamp)
reason = bot.calendar_filter.get_blackout_reason(timestamp)
print(f"Blackout: {blackout}, Reason: {reason}")

# Session
rth = bot.session_filter.is_rth_session(timestamp)
print(f"RTH session: {rth}")
```

## 📈 Prochaines Étapes (Hors Scope v1)

1. **Récupérer données réelles CME**
   - Intégrer API Rithmic pour données tick
   - Gérer rollovers contrats

2. **Backtest 50+ trades**
   - Valider logique
   - Vérifier edge cases

3. **Analyser filtre impact**
   - Perf avec/sans macro filter
   - Perf avec/sans calendar filter
   - Quantifier amélioration DD

4. **Stress test**
   - Slippage 1-2 ticks
   - Commissions CME (1 tick/side typical)
   - Vérifier profitabilité survit

5. **Live trading**
   - Implémenter API Rithmic complète
   - Connect TopstepX
   - Paper trading validation
   - GO live après 6 mois stable backtest

## ⚠️ Règles à Respecter

```
❌ Pas d'ajout setup avant 50+ trades
❌ Pas de trailing stop
❌ Pas d'optimisation paramètre par paramètre
❌ Pas de live sans 6+ mois backtest
```

Chaque exception détruit crédibilité fund future.

---

**Version**: v1 FROZEN  
**Date**: 6 février 2026  
**Modification**: Interdite sans approbation explicite
