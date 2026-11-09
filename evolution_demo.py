#!/usr/bin/env python3
"""
Example usage of the enhanced trading bot with evolutionary backtesting.
"""

from main import TradingBot

def main():
    print("=== Trading Bot Evolutionary Backtest Demo ===")
    
    # Initialize the trading bot
    bot = TradingBot()
    
    # Example: Run evolutionary backtest for BTC futures over 10 generations (small test)
    try:
        print("\nStarting evolutionary backtest...")
        
        # Run a small test with just 10 generations to demonstrate functionality
        results = bot.evolve_backtest(
            instrument="BTC",
            start_date="2024-01-01",
            end_date="2024-03-01", 
            generations=10,  # Reduced for demo purposes
            population_size=10,
            mutation_rate=0.2
        )
        
        print(f"\nEvolutionary backtest completed!")
        print(f"Best fitness score: {results['best_fitness']}")
        print(f"Best parameters found: {results['best_parameters']}")
        
    except Exception as e:
        print(f"Error running evolutionary backtest: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()