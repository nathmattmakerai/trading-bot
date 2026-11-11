# FTMO Trading Bot System

A comprehensive trading bot system for futures, stocks, and crypto markets with advanced backtesting capabilities.

## Architecture Overview

```
TradingBot (main orchestrator)
├── Data Collection
│   ├── crawler.py (web crawler for financial data)
│   ├── stock_data_loader.py
│   ├── futures_data_loader.py
│   └── macro_data_loader.py
├── Backtesting Engine
│   └── engine_futures.py
├── Trading Logic
│   ├── filters/
│   │   ├── macro_filter.py
│   │   ├── calendar_filter.py
│   │   └── session_filter.py
│   ├── structure/
│   │   └── compression_detector.py
│   ├── setup/
│   │   └── breakout_v1.py
│   └── risk/
│       ├── position_sizer.py
│       └── equity_guard.py
└── Learning System
    └── error_analyzer.py
```

## Key Features

### 1. Data Collection
- **Web Crawler**: Collects stock, crypto, and futures data from Yahoo Finance
- **Market Sentiment**: Analyzes sentiment for different asset classes
- **Technical Indicators**: Calculates SMA, EMA, MACD, RSI, Bollinger Bands
- **Flexible Data Sources**: Supports multiple financial data providers

### 2. Trading Logic
- **Compression Detection**: Identifies market consolidation patterns
- **Breakout Setup**: Detects breakout signals with confidence levels
- **Multi-Filters**: Macro, Calendar, and Session filters
- **Risk Management**: Position sizing, stop-loss, take-profit calculations
- **Equity Guard**: Adaptive capital protection

### 3. Backtesting System
- **Comprehensive Statistics**: Win rate, profit factor, Sharpe ratio, etc.
- **Walk-Forward Analysis**: Robust testing across time periods
- **Parameter Optimization**: Testing different strategy parameters
- **Virtual Trade Handling**: Distinguishes real vs virtual trades

### 4. Learning & Adaptation
- **Error Analyzer**: Learns from trade outcomes
- **Adaptive Strategy Selection**: Adjusts approach based on market conditions
- **Performance Diagnostics**: Identifies strengths and weaknesses

## Installation

```bash
# Install required packages
pip install pandas numpy yfinance requests

# Clone the repository
git clone <repository-url>
cd trading-bot
```

## Usage

### Running Demo
```bash
python demo_data_collection.py
```

### Basic Backtesting
```python
from main import TradingBot

# Initialize bot
bot = TradingBot(starting_balance=10000.0)

# Run backtest
bot.backtest("NQ", "2024-01-01", "2024-12-31")
```

### Data Collection
```python
from data.crawler import FinancialDataCrawler

# Crawl financial data
crawler = FinancialDataCrawler()
data = crawler.crawl_all_data(period="6mo")

# Save collected data
crawler.save_data(data, "collected_data.json")
```

## Core Components

### 1. TradingBot
Main orchestrator that coordinates all components.

### 2. Data Loaders
- `FuturesDataLoader`: Loads futures data
- `StockDataLoader`: Loads stock data  
- `MacroDataLoader`: Loads macroeconomic indicators

### 3. Backtesting Engine
- `BacktestEngine`: Core backtesting functionality
- `BacktestRunner`: Enhanced runner with statistics and analysis

### 4. Trading Logic Components
- **Filters**: Apply market conditions (macro, calendar, session)
- **Structure**: Detect compression patterns
- **Setup**: Identify breakout opportunities
- **Risk Management**: Position sizing and capital protection

## Configuration

Default configurations are stored in `config/rules_v1.py`. You can customize:
- Risk parameters
- Breakout detection settings  
- Filter conditions
- Position sizing rules

## Testing

Run integration tests:
```bash
python test_integration.py
```

Run demo:
```bash
python demo_data_collection.py
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

MIT License