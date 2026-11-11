"""
Integration example showing how RiskEngine works with the broker system
"""

from risk_engine import RiskEngine
from broker.base_broker import Order, SimulationBroker

# Example of integrating risk engine with existing broker system
def example_integration():
    # Initialize risk engine
    risk_engine = RiskEngine(initial_equity=100000.0)

    # Create a simulation broker (similar to what exists in the project)
    broker = SimulationBroker()

    # Simulate a trading scenario
    print("Initial equity:", risk_engine.current_equity)

    # Calculate position size using risk engine
    symbol = "NQ"
    entry_price = 18000.0
    stop_loss_distance = 50.0

    position_size, risk_amount = risk_engine.calculate_position_size(
        symbol=symbol,
        entry_price=entry_price,
        stop_loss_distance=stop_loss_distance
    )

    print(f"Calculated position size: {position_size:.2f}")
    print(f"Risk amount per trade: ${risk_amount:.2f}")

    # Validate the trade with risk engine
    validation_status = risk_engine.validate_trade(
        symbol=symbol,
        entry_price=entry_price,
        stop_loss_distance=stop_loss_distance
    )

    if validation_status == "acceptable":
        print("Trade validated successfully")

        # Execute the trade through broker (with risk engine controls)
        order = Order(
            order_id=1,
            instrument=symbol,
            direction="long",
            size=int(position_size),
            price=entry_price,
            stop_loss=entry_price - stop_loss_distance,
            take_profit=entry_price + (stop_loss_distance * 2),  # Example TP
            timestamp="now"
        )

        # Submit order through broker (risk engine controls are applied)
        success = broker.submit_order(order)
        print(f"Order submitted: {success}")

        # Update risk metrics after trade
        if success:
            print("Trade executed successfully")
            print("Current risk metrics:")
            metrics = risk_engine.get_risk_metrics()
            for key, value in metrics.items():
                print(f"  {key}: {value}")
    else:
        print(f"Trade validation failed: {validation_status}")

if __name__ == "__main__":
    example_integration()