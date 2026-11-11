# Risk Management Module

This module implements centralized risk management controls that cannot be bypassed by strategies.

## Features

- **Dynamic Position Sizing**: Calculates position sizes based on equity, stop loss distance, and volatility
- **Risk Firewalls**: Implements multiple risk controls to prevent excessive exposure
- **Daily Loss Tracking**: Monitors daily losses to prevent catastrophic drawdowns
- **Total Risk Exposure**: Tracks overall portfolio risk across all positions
- **Trade Validation**: Validates trades against risk parameters before execution

## Core Components

### RiskEngine
The main class that manages all risk controls and position sizing calculations.

### RiskParameters
Configuration class for defining risk limits and constraints.

### Position
Data class representing a trading position with relevant details.

## Risk Controls

1. **Max Risk Per Trade**: Limits risk per individual trade (default 0.75% of equity)
2. **Max Daily Loss**: Limits total daily losses (default 2.5% of equity)
3. **Max Position Size**: Limits any single position to a percentage of equity (default 10%)
4. **Max Total Risk**: Limits overall portfolio risk exposure (default 5% of equity)

## Usage

```python
from risk_engine import RiskEngine

# Initialize risk engine
risk_engine = RiskEngine(initial_equity=100000.0)

# Calculate position size
position_size, risk_amount = risk_engine.calculate_position_size(
    symbol="NQ",
    entry_price=18000.0,
    stop_loss_distance=50.0
)

# Validate and execute trade
success = risk_engine.execute_trade(
    symbol="NQ",
    entry_price=18000.0,
    stop_loss_distance=50.0,
    quantity=position_size
)
```

## Testing

Run unit tests with:
```bash
python -m unittest risk/test_risk_engine.py
```