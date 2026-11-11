"""
Risk Management Engine for Trading Bot

This module implements centralized risk management with dynamic position sizing
and risk firewalls that cannot be bypassed by strategies.
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Position:
    """Represents a trading position"""
    symbol: str
    quantity: float
    entry_price: float
    side: str  # 'long' or 'short'
    entry_time: str

@dataclass
class RiskParameters:
    """Risk parameters for position sizing and controls"""
    max_risk_per_trade_percent: float = 0.75  # 0.75% per trade
    max_daily_loss_percent: float = 2.5       # 2.5% daily max loss
    max_position_size_percent: float = 10.0   # Maximum 10% of equity in any single position
    max_total_risk_percent: float = 5.0       # Maximum 5% of equity in total risk

class RiskStatus(Enum):
    """Enumeration for risk status"""
    ACCEPTABLE = "acceptable"
    EXCESSIVE_RISK = "excessive_risk"
    MAX_POSITION_SIZE_EXCEEDED = "max_position_size_exceeded"
    MAX_DAILY_LOSS_EXCEEDED = "max_daily_loss_exceeded"

class RiskEngine:
    """
    Centralized risk management system that manages position sizes,
    exposures, and implements risk firewalls.
    """

    def __init__(self, initial_equity: float = 100000.0):
        """
        Initialize the risk engine

        Args:
            initial_equity (float): Starting equity amount
        """
        self.initial_equity = initial_equity
        self.current_equity = initial_equity
        self.position_size_percent = 0.0
        self.daily_loss = 0.0
        self.total_risk_exposure = 0.0
        self.positions: Dict[str, Position] = {}
        self.risk_params = RiskParameters()
        self.trade_history: List[Dict] = []

    def update_equity(self, new_equity: float) -> None:
        """
        Update current equity level

        Args:
            new_equity (float): New equity value
        """
        self.current_equity = new_equity

    def calculate_position_size(self,
                              symbol: str,
                              entry_price: float,
                              stop_loss_distance: float,
                              volatility: float = 1.0) -> Tuple[float, float]:
        """
        Calculate appropriate position size based on risk parameters

        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price of the trade
            stop_loss_distance (float): Distance to stop loss level
            volatility (float): Volatility factor for adjustment

        Returns:
            Tuple[float, float]: Position size and risk amount
        """
        # Calculate risk per trade based on equity and risk parameters
        max_risk_per_trade = self.current_equity * (self.risk_params.max_risk_per_trade_percent / 100)

        # Calculate position size using stop loss distance
        if stop_loss_distance <= 0:
            raise ValueError("Stop loss distance must be positive")

        risk_amount = max_risk_per_trade
        position_size = risk_amount / (stop_loss_distance * volatility)

        # Apply maximum position size constraint
        max_position_size = self.current_equity * (self.risk_params.max_position_size_percent / 100)
        position_size = min(position_size, max_position_size / entry_price)

        return position_size, risk_amount

    def validate_trade(self,
                      symbol: str,
                      entry_price: float,
                      stop_loss_distance: float,
                      volatility: float = 1.0) -> RiskStatus:
        """
        Validate if a trade is within acceptable risk parameters

        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price of the trade
            stop_loss_distance (float): Distance to stop loss level
            volatility (float): Volatility factor for adjustment

        Returns:
            RiskStatus: Status indicating if trade is acceptable
        """
        # Calculate risk amount for this potential trade
        max_risk_per_trade = self.current_equity * (self.risk_params.max_risk_per_trade_percent / 100)
        risk_amount = max_risk_per_trade

        # Check if total risk exposure would exceed limits
        if self.total_risk_exposure + risk_amount > self.current_equity * (self.risk_params.max_total_risk_percent / 100):
            return RiskStatus.EXCESSIVE_RISK

        # Calculate position size to check against max position size limit
        position_size = risk_amount / (stop_loss_distance * volatility)
        max_position_size = self.current_equity * (self.risk_params.max_position_size_percent / 100)

        if position_size > max_position_size / entry_price:
            return RiskStatus.MAX_POSITION_SIZE_EXCEEDED

        # Check daily loss limit
        if self.daily_loss + risk_amount > self.current_equity * (self.risk_params.max_daily_loss_percent / 100):
            return RiskStatus.MAX_DAILY_LOSS_EXCEEDED

        return RiskStatus.ACCEPTABLE

    def execute_trade(self,
                     symbol: str,
                     entry_price: float,
                     stop_loss_distance: float,
                     quantity: float,
                     side: str = 'long',
                     volatility: float = 1.0) -> bool:
        """
        Execute a trade after risk validation

        Args:
            symbol (str): Trading symbol
            entry_price (float): Entry price of the trade
            stop_loss_distance (float): Distance to stop loss level
            quantity (float): Number of contracts/units to trade
            side (str): 'long' or 'short'
            volatility (float): Volatility factor for adjustment

        Returns:
            bool: True if trade executed successfully, False otherwise
        """
        # Validate the trade first
        risk_status = self.validate_trade(symbol, entry_price, stop_loss_distance, volatility)

        if risk_status != RiskStatus.ACCEPTABLE:
            logger.warning(f"Trade validation failed for {symbol}: {risk_status.value}")
            return False

        # Calculate risk amount and update exposure
        risk_amount = quantity * stop_loss_distance * volatility

        # Update position tracking
        self.positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=entry_price,
            side=side,
            entry_time="now"  # In a real system, this would be actual timestamp
        )

        # Update risk exposure metrics
        self.total_risk_exposure += risk_amount
        self.daily_loss += risk_amount

        # Record trade in history
        trade_record = {
            'symbol': symbol,
            'entry_price': entry_price,
            'quantity': quantity,
            'side': side,
            'stop_loss_distance': stop_loss_distance,
            'risk_amount': risk_amount,
            'timestamp': "now"  # In a real system, this would be actual timestamp
        }
        self.trade_history.append(trade_record)

        logger.info(f"Trade executed for {symbol}: {quantity} contracts at ${entry_price}")
        return True

    def close_position(self, symbol: str, exit_price: float) -> float:
        """
        Close a position and calculate profit/loss

        Args:
            symbol (str): Trading symbol
            exit_price (float): Exit price of the trade

        Returns:
            float: Profit or loss amount
        """
        if symbol not in self.positions:
            logger.warning(f"No position found for {symbol}")
            return 0.0

        position = self.positions[symbol]

        # Calculate profit/loss
        if position.side == 'long':
            profit_loss = (exit_price - position.entry_price) * position.quantity
        else:  # short position
            profit_loss = (position.entry_price - exit_price) * position.quantity

        # Update equity
        self.current_equity += profit_loss

        # Remove position from tracking
        del self.positions[symbol]

        logger.info(f"Position closed for {symbol}: ${profit_loss:.2f}")
        return profit_loss

    def get_risk_metrics(self) -> Dict:
        """
        Get current risk metrics

        Returns:
            Dict: Dictionary of current risk metrics
        """
        return {
            'current_equity': self.current_equity,
            'initial_equity': self.initial_equity,
            'daily_loss': self.daily_loss,
            'total_risk_exposure': self.total_risk_exposure,
            'risk_ratio': self.total_risk_exposure / self.current_equity if self.current_equity > 0 else 0.0,
            'position_count': len(self.positions),
            'max_daily_loss_percent': self.risk_params.max_daily_loss_percent
        }

    def reset_daily_metrics(self) -> None:
        """
        Reset daily loss tracking for new trading day
        """
        self.daily_loss = 0.0
        logger.info("Daily risk metrics reset")

    def set_risk_parameters(self, params: RiskParameters) -> None:
        """
        Set new risk parameters

        Args:
            params (RiskParameters): New risk parameters to use
        """
        self.risk_params = params
        logger.info("Risk parameters updated")

# Example usage and testing
if __name__ == "__main__":
    # Initialize risk engine
    risk_engine = RiskEngine(initial_equity=100000.0)

    # Test position sizing
    position_size, risk_amount = risk_engine.calculate_position_size(
        symbol="NQ",
        entry_price=18000.0,
        stop_loss_distance=50.0,
        volatility=1.0
    )

    print(f"Position size: {position_size:.2f}")
    print(f"Risk amount: ${risk_amount:.2f}")

    # Test trade validation
    risk_status = risk_engine.validate_trade(
        symbol="NQ",
        entry_price=18000.0,
        stop_loss_distance=50.0,
        volatility=1.0
    )

    print(f"Trade validation status: {risk_status.value}")

    # Test trade execution
    success = risk_engine.execute_trade(
        symbol="NQ",
        entry_price=18000.0,
        stop_loss_distance=50.0,
        quantity=position_size,
        side='long',
        volatility=1.0
    )

    print(f"Trade execution successful: {success}")

    # Display risk metrics
    metrics = risk_engine.get_risk_metrics()
    print("Risk Metrics:")
    for key, value in metrics.items():
        print(f"  {key}: {value}")