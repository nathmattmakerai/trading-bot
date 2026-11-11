# Trading Bot Architecture Summary

## Overview
This is an intraday futures trading bot designed for NQ (Nasdaq 100) and ES (S&P 500) futures contracts. The system implements a systematic approach to trading with multiple layers of risk management, filters, and learning capabilities.

## Core Components

### 1. Main Trading Bot (`main.py`)
- **Core orchestration**: Coordinates all components
- **Backtesting framework**: Processes historical data through the complete trading pipeline
- **Risk management integration**: Implements strict risk rules (0.75% per trade, 2.5% daily max loss)
- **Position sizing**: Calculates contract sizes based on risk parameters

### 2. Data Management (`data/` directory)
- **Futures Data Loader**: Loads historical futures data from CME
- **Macro Data Loader**: Fetches macroeconomic indicators (VIX, US10Y yield)
- **Calendar Loader**: Handles trading calendar and blackout events
- **Sentiment Analyzer**: Analyzes market sentiment (fallback to mock data)
- **Financial Data Crawler**: Web crawler for collecting financial data from various sources

### 3. Engine Components (`engine/` directory)

#### Backtesting Engine (`engine/backtest/`)
- Simulates trading on historical data
- Manages open/closed trades
- Calculates performance statistics

#### Filters (`engine/filters/`)
- **Macro Filter**: Uses VIX and yield data to determine risk regime (risk-on vs risk-off)
- **Calendar Filter**: Prevents trading during blackout events (FOMC, CPI, NFP, etc.)
- **Session Filter**: Only trades during specified hours (8:00 AM - 3:00 PM ET)

#### Setup Detection (`engine/setup/`)
- **Breakout v1**: Implements bidirectional breakout detection after compression
- Uses compression detection to identify potential breakout opportunities

#### Structure Analysis (`engine/structure/`)
- **Compression Detector**: Identifies periods of low volatility (compression)
- Uses ATR (Average True Range) comparisons to detect compression patterns

#### Risk Management (`engine/risk/`)
- **Position Sizer**: Calculates optimal position sizes based on risk parameters
- Implements strict risk rules: 0.75% per trade, 2.5% daily max loss, max 2 trades/day
- Handles stop-loss and take-profit calculations (3R fixed ratio)

### 4. Broker Integration (`broker/`)
- **Simulation Broker**: For backtesting purposes
- **Rithmic Broker**: Adapter for live trading with TopstepX/Rithmic prop firm

## Trading Logic Flow

1. **Data Collection**: Load historical futures, macroeconomic, and calendar data
2. **Compression Detection**: Identify periods of low volatility 
3. **Breakout Detection**: Wait for price action to break out of compression range
4. **Filter Validation**: Apply macroeconomic and calendar filters
5. **Position Sizing**: Calculate optimal contract size based on risk management rules
6. **Execution**: Place orders with calculated stop-loss and take-profit levels
7. **Risk Management**: Enforce strict position limits and daily loss controls

## Key Features

### Risk Management
- 0.75% risk per trade (fixed percentage of account)
- Maximum 2.5% drawdown per day
- Maximum 2 trades per day
- One-trade-at-a-time rule
- 3R fixed reward-to-risk ratio

### Filters
- Macroeconomic filters based on VIX and yield curves
- Calendar blackout events for major economic releases
- Trading session restrictions (8:00 AM - 3:00 PM ET)

### Learning & Adaptation
- Market sentiment analysis capabilities
- Technical indicator calculations
- Data collection and crawling functionality

## Configuration
The system uses a frozen configuration (`config/rules_v1.py`) that defines:
- Instruments: NQ and ES futures
- Timeframes: 15-minute base timeframe
- Risk parameters: Strict risk management rules
- Trading sessions: Specific hours for trading
- Setup rules: Breakout after compression detection

## Data Sources
- Futures prices from CME
- VIX data from Yahoo Finance/Bloomberg
- US10Y yield from US Treasury/Federal Reserve
- Economic calendar from Investing.com

## Architecture Strengths
1. **Modular Design**: Each component has a specific responsibility
2. **Backtesting Capability**: Full simulation of trading strategies
3. **Risk Management**: Strict rules prevent catastrophic losses
4. **Filter Integration**: Multiple layers of validation before trading
5. **Scalability**: Easy to add new data sources or trading logic

## Usage Pattern
The bot is designed for systematic intraday trading with a focus on:
- Compression breakout patterns
- Risk-controlled position sizing
- Multi-layer filtering to avoid poor market conditions
- Automated backtesting and performance evaluation