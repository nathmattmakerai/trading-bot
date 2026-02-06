"""
PRE-BACKTEST CHECKLIST

À vérifier avant de lancer backtests pour la première fois.
"""

def main():
    """Main checklist."""
    
    print("\n" + "="*80)
    print("PRE-BACKTEST CHECKLIST")
    print("="*80 + "\n")
    
    checklist = {
        "🔧 Environment Setup": [
            ("Python 3.9+", "python --version"),
            ("Virtual env activated", "which python"),
            ("Requirements installed", "pip list | grep pandas"),
        ],
        
        "📦 Module Imports": [
            ("config.rules_v1", "import config.rules_v1"),
            ("data loaders", "import data.futures_data_loader"),
            ("macro filter", "from engine.filters.macro_filter import MacroFilter"),
            ("calendar filter", "from engine.filters.calendar_filter import CalendarFilter"),
            ("session filter", "from engine.filters.session_filter import SessionFilter"),
            ("compression detector", "from engine.structure.compression_detector import CompressionDetector"),
            ("breakout setup", "from engine.setup.breakout_v1 import BreakoutSetupV1"),
            ("position sizer", "from engine.risk.position_sizer import PositionSizer"),
            ("backtest engine", "from engine.backtest.engine_futures import BacktestEngine"),
            ("trading bot", "from main import TradingBot"),
        ],
        
        "🧪 Unit Tests": [
            ("All tests pass", "python -m pytest tests/validation_suite.py"),
        ],
        
        "🧮 Quick Test": [
            ("Bot initializes", "TradingBot(10000)"),
            ("Compression detector works", "is_compression(df)"),
            ("Breakout signal works", "get_breakout_signal(df)"),
            ("Position sizing works", "calculate_position_size(10000, 25, 100, 95)"),
        ],
        
        "📊 Data Verification": [
            ("Yahoo Finance accessible", "yf.download('^VIX', ...)"),
            ("NQ/ES data loadable", "fetch_futures_data('NQ', ...)"),
            ("VIX data loadable", "fetch_vix(...)"),
            ("US10Y data loadable", "fetch_us10y_yield(...)"),
            ("Calendar dates loaded", "CalendarLoader().fomc_dates"),
        ],
        
        "✅ Configuration": [
            ("rules_v1 accessible", "from config.rules_v1 import *"),
            ("All params defined", "COMPRESSION_CONFIG, RISK_CONFIG, etc"),
            ("No modifications made", "Check VERSION = 'v1_FROZEN'"),
            ("Locked = True", "LOCKED == True"),
        ],
        
        "📈 Backtest Prerequisites": [
            ("Starting balance set", "starting_balance = 10000"),
            ("Date range valid", "start < end, both YYYY-MM-DD"),
            ("Instrument valid", "instrument in ['NQ', 'ES']"),
            ("Enough historical data", "1+ year of data available"),
        ],
        
        "📝 Documentation": [
            ("README.md reviewed", "Know how to run bot"),
            ("TECHNICAL_DOCS.md reviewed", "Understand architecture"),
            ("example_backtest.py reviewed", "Know output format"),
        ],
    }
    
    completed = 0
    total = sum(len(items) for items in checklist.values())
    
    for section, items in checklist.items():
        print(f"\n{section}")
        print("-" * 80)
        
        for item, check in items:
            status = "[ ] PENDING"
            print(f"  {status}  {item}")
            print(f"          → {check}")
        
        print()
    
    print("="*80)
    print(f"Total items: {total}")
    print("="*80 + "\n")
    
    print("INSTRUCTIONS:")
    print("-" * 80)
    print("1. Go through each checklist item")
    print("2. Run the verification command")
    print("3. Mark [ ] as [X] when complete")
    print("4. If any item fails, debug and fix before proceeding")
    print("5. Once all checked, you're ready for backtest!")
    print()
    
    print("TO RUN BACKTEST:")
    print("-" * 80)
    print("python example_backtest.py")
    print()
    
    print("For custom backtest:")
    print("```python")
    print("from main import TradingBot")
    print("bot = TradingBot(starting_balance=10000)")
    print("stats = bot.backtest(")
    print("    instrument='NQ',")
    print("    start_date='2024-01-01',")
    print("    end_date='2024-12-31'")
    print(")")
    print("print(stats)")
    print("```")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
