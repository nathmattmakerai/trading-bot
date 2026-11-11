# Module Documentation

This document provides detailed information about each module in the trading bot system.

## 1. core/
### Purpose
The core module serves as the main orchestrator of the trading system, coordinating all other modules and managing the overall flow of execution.

### Responsibilities
- System initialization and configuration
- Integration of all subsystems
- Main execution loop control
- Error handling and logging

### Key Components
- TradingBot class (main orchestrator)
- System startup and shutdown procedures
- Configuration management

## 2. data/
### Purpose
The data module handles all aspects of data loading, processing, and validation for the trading system.

### Responsibilities
- Loading historical and real-time market data
- Supporting multiple data sources (Yahoo Finance, CME, economic calendars)
- Data cleaning and validation
- Data transformation and resampling

### Key Components
- FuturesDataLoader
- MacroDataLoader  
- CalendarLoader
- Data validation utilities

## 3. market_intelligence/
### Purpose
The market intelligence module provides a coherent representation of current market conditions to other system components.

### Responsibilities
- Aggregating price, volume, volatility, liquidity, trends, correlations, sentiment, regimes, and events
- Automated regime detection and transition prediction
- Market state analysis

### Key Components
- MarketBrain engine
- RegimeDetector
- MarketConditionAnalyzer

## 4. strategies/
### Purpose
The strategies module implements and manages different trading approaches.

### Responsibilities
- Multiple strategy support
- Independent signal generation with confidence levels
- Strategy competition and selection
- Signal conflict resolution

### Key Components
- StrategyBase class
- StrategyEngine
- SignalGenerator
- StrategySelector

## 5. genetic/
### Purpose
The genetic module provides evolutionary optimization capabilities for the trading system.

### Responsibilities
- Multi-objective fitness functions
- Evolutionary robustness measures
- Prevention of premature convergence
- Genetic algorithm implementation

### Key Components
- GeneticEngine
- FitnessCalculator
- EvolutionManager

## 6. sentiment/
### Purpose
The sentiment module analyzes market sentiment from public sources.

### Responsibilities
- Free and reliable sentiment analysis
- Source reliability scoring
- Data validation and quality control
- Integration with market intelligence

### Key Components
- SentimentAnalyzer
- SourceReliabilityScorer
- SentimentAggregator

## 7. risk/
### Purpose
The risk module implements centralized risk management controls.

### Responsibilities
- Position sizing with dynamic parameters
- Risk firewalls before order execution
- Compliance with strict risk rules
- Adaptive protection mechanisms

### Key Components
- RiskEngine
- PositionSizer
- EquityGuard
- RiskFirewall

## 8. portfolio/
### Purpose
The portfolio module manages multi-asset allocation and performance tracking.

### Responsibilities
- Portfolio optimization
- Multi-asset position management
- Performance attribution
- Risk allocation across assets

### Key Components
- PortfolioManager
- AssetAllocator
- PerformanceTracker

## 9. execution/
### Purpose
The execution module handles order processing and broker integration.

### Responsibilities
- Order execution logic
- Broker integration (simulation and live)
- Transaction cost handling
- Execution quality monitoring

### Key Components
- ExecutionEngine
- BrokerInterface
- OrderProcessor

## 10. backtesting/
### Purpose
The backtesting module provides realistic simulation capabilities.

### Responsibilities
- Backtesting with transaction costs and slippage
- Realistic order execution simulation
- Performance analysis and reporting
- Strategy validation

### Key Components
- BacktestEngine
- SimulationFramework
- PerformanceAnalyzer

## 11. learning/
### Purpose
The learning module enables continuous improvement through experience.

### Responsibilities
- Decision replay and memory of mistakes
- Performance attribution
- Adaptive confidence adjustment
- System self-improvement

### Key Components
- LearningEngine
- ErrorAnalyzer
- MemoryManager
- ConfidenceAdjuster

## 12. api/
### Purpose
The API module provides system control and monitoring interfaces.

### Responsibilities
- REST API endpoints
- Dashboard interfaces
- External integration points
- System monitoring access

### Key Components
- APIRouter
- DashboardInterface
- MonitoringAPI

## 13. monitoring/
### Purpose
The monitoring module ensures system reliability and early problem detection.

### Responsibilities
- CPU, RAM, storage monitoring
- API and connection status tracking
- Error logging and alerting
- Recovery mechanisms

### Key Components
- SystemMonitor
- AlertEngine
- HealthChecker
- LogManager

## 14. tests/
### Purpose
The tests module contains all unit, integration, and regression tests.

### Responsibilities
- Unit testing for each component
- Integration testing
- Regression testing
- Test automation

### Key Components
- UnitTestSuite
- IntegrationTestFramework
- RegressionTester