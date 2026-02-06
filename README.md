# FTMO Trading Bot - PRD v1 (FROZEN)

Algorithmic futures trading bot (NQ/ES) basé sur un setup unique de breakout compression avec risk management strict et filtrage macro. Conçu pour prop firm trading (FTMO, TopstepX).

## 📋 Architecture Figée

Toute cette architecture est **GELÉE pour v1**. Aucune modification sans approbation explicite.

```
ftmo_futures_bot/
├── config/
│   └── rules_v1.py              # PRD codé (GELÉ)
│
├── data/
│   ├── futures_data_loader.py   # NQ/ES 15m/H1/H4
│   └── macro_data_loader.py     # VIX + US10Y
│   └── calendar_loader.py       # FOMC/NFP/CPI/Rollover
│
├── engine/
│   ├── filters/
│   │   ├── macro_filter.py      # VIX-based risk regime
│   │   ├── calendar_filter.py   # Event blackout
│   │   └── session_filter.py    # RTH only
│   │
│   ├── structure/
│   │   └── compression_detector.py  # ATR-based range
│   │
│   ├── setup/
│   │   └── breakout_v1.py       # Setup unique
│   │
│   ├── risk/
│   │   └── position_sizer.py    # 0.75% risk, whole contracts
│   │
│   └── backtest/
│       └── engine_futures.py    # Moteur principal
│
├── broker/
│   ├── base_broker.py           # Interface générique
│   └── rithmic_broker.py        # TopstepX (simulation)
│
├── main.py                      # Orchestrateur
└── tests/
    └── validation_suite.py      # Tests unitaires
```

## 🎯 Paramètres Figés v1

### Timeframe
- **Trading**: 15 minutes
- **Context**: 1H, 4H
- **Macro**: Daily

### Setup Unique
Breakout bidirectionnel de compression

**Détection compression** (ATR-based):
```
ATR(14) < 0.75 × ATR(50)           ✓
Range(20) < 1.5 × ATR(14)          ✓
```

**Breakout confirmé**:
```
Long:  close > max(high[-20:])
Short: close < min(low[-20:])
```

### Instruments
- NQ (Nasdaq 100 futures)
- ES (S&P 500 futures)
- **One-trade-at-a-time**: Une seule position ouverte

### Risk Management
```
Risk/trade:      0.75%
Max daily loss:  2.5%
Max trades/day:  2
SL:              Côté opposé du range
TP:              Fixe à 3R (pas de trailing)
```

### Filtres Obligatoires
1. **Session**: RTH US uniquement (8:00 AM - 3:00 PM ET)
2. **Calendrier**: Blackout FOMC, CPI, NFP, Rollover (veille + lendemain)
3. **Macro**: 
   - VIX < 18 & yields ↑ = Long autorisé
   - VIX > 22 ou yields ↓ = Short only
   - Entre les deux = Sélectif

### KPI Cibles
- Drawdown max: < 3.5%
- Retour monthly: ≥ 5% en moyenne
- Track record: ≥ 6 mois stable

## 🚀 Installation

```bash
# Clone repo
git clone https://github.com/nathmattmakerai/trading-bot.git
cd trading-bot

# Python 3.9+
python -m venv venv
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate  # Windows

# Install dépendences
pip install -r requirements.txt
```

## 📚 Dépendences

```
pandas>=1.5.0
numpy>=1.23.0
yfinance>=0.2.28
pandas-ta>=0.3.14b0
```

## 🧪 Tests Unitaires

```bash
# Run full test suite
python -m pytest tests/validation_suite.py -v

# Run spécific test
python -m pytest tests/validation_suite.py::TestCompressionDetector -v
```

## 📊 Backtest

### Étape 1: Backtest brut (setup seul)

```python
from main import TradingBot

bot = TradingBot(starting_balance=10000)
stats = bot.backtest(
    instrument="NQ",
    start_date="2024-01-01",
    end_date="2024-12-31",
)

print(f"Total trades: {stats['num_trades']}")
print(f"Win rate: {stats['win_rate']:.1f}%")
print(f"Max DD: {stats['max_drawdown_pct']:.2f}%")
```

### Étape 2: Analyse AVEC/SANS filtres

Compare performance:
- Setup seul
- Setup + filtre calendrier
- Setup + filtre macro
- Setup + tous filtres

### Étape 3: Stress test

- Slippage 1-2 ticks
- Commissions CME réalistes
- Vérifier survie du système

## 🔁 Logique Système (Résumé Exécutable)

À chaque close de bougie 15m:

```
1. Vérifier session RTH autorisée
2. Vérifier pas de blackout calendrier
3. Vérifier filtre macro compatible
4. Vérifier pas de position ouverte (one-at-a-time)
5. Vérifier max trades/jour et daily loss
6. Détecter compression
7. Détecter breakout confirmé
8. Calculer SL (côté opposé range) + TP (3R)
9. Calculer taille position (0.75% risk, whole contracts)
10. Exécuter trade
11. Gérer jusqu'à TP / SL / fin de session
```

## ⚙️ Configuration

Tous les paramètres sont dans `config/rules_v1.py`:

```python
COMPRESSION_CONFIG = {
    "atr_period": 14,
    "atr_ratio_threshold": 0.75,
    "range_lookback_period": 20,
    "range_ratio_threshold": 1.5,
}

RISK_CONFIG = {
    "risk_per_trade": 0.0075,  # 0.75%
    "max_daily_loss": 0.025,   # 2.5%
    "max_trades_per_day": 2,
}

# ... plus de config figée
```

**⚠️ AUCUNE MODIFICATION** sans approbation.

## 🛡️ Règles Anti-Ego (PROTECTION)

Ces règles vous protègent de vous-mêmes:

```
❌ Pas d'ajout de setup avant 50+ trades backtestés
❌ Pas de "juste un petit trailing"
❌ Pas d'optimisation paramètre par paramètre
❌ Pas de live sans backtest stable sur 6+ mois

Chaque exception tue un futur fund manager.
```

## 🔌 Broker Integration (TopstepX / FTMO)

### Simulation (Backtest)
```python
from broker.base_broker import SimulationBroker

broker = SimulationBroker()
# Exécution immédiate pour backtest
```

### Live (TopstepX)
```python
from broker.base_broker import RithmicBroker

broker = RithmicBroker(connection_params={
    "username": "your_user",
    "password": "your_pass",
    # ... config Rithmic
})
broker.connect()
```

*Note: API Rithmic à implémenter (placeholder disponible)*

## 📈 Monitoring & Logging

Le bot log automatiquement:
- Chaque trade exécutée
- Chaque raison filtre (pourquoi pas de trade)
- Equity curve
- PnL quotidien

```python
# Accéder equity curve
equity_df = bot.backtest_engine.get_equity_curve()
equity_df.plot()  # Visualise courbe
```

## 🐛 Debugging

```python
# Accéder aux statistiques détaillées
stats = bot.backtest_engine.get_statistics()
print(stats)

# Accéder à toutes les trades fermées
for trade in bot.backtest_engine.closed_trades:
    print(f"Trade #{trade.trade_id}: {trade.direction} "
          f"{trade.pnl:.2f} ({trade.pnl_pct:.1f}%)")
```

## 📝 Checklist Technique

- [x] Données: NQ/ES 15m + contexte H1/H4
- [x] Macro: VIX + US10Y daily
- [x] Calendrier: FOMC/CPI/NFP/Rollover blackout
- [x] Setup: Compression ATR + Breakout
- [x] Filtres: Session, Calendrier, Macro
- [x] Risk: Position sizer 0.75%, max 2.5% DD daily
- [x] Backtest: Engine avec equity curve
- [x] Broker: Simulation + placeholder Rithmic
- [x] Tests: Validation suite complète
- [ ] **PROCHAINES ÉTAPES**:
  - [ ] Récupérer données réelles CME
  - [ ] Backtest 50+ trades
  - [ ] Valider filtre améliore DD
  - [ ] Stress test (slippage, commissions)
  - [ ] Approuver pour live trading

## 📞 Support

Pour toute question ou issue:
1. Vérifier console pour logs
2. Vérifier tests unitaires (`tests/validation_suite.py`)
3. Consulter docstrings du code

## 📄 License

Propriétaire. Utilisation restreinte à trading personnel/prop firm.

---

**Version**: v1 (FROZEN)  
**Date de création**: 6 février 2026  
**Locked**: ✅ OUI

Chaque modification doit passer par code review explicite.
