"""
Risk Management Module for Futures Trading Bot
This module handles position sizing, stop-losses, take-profits, and other risk controls.
"""

import logging
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Data class to represent a trade"""
    instrument: str
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    timestamp: str
    trade_type: str  # 'long' or 'short'

class RiskManager:
    """
    Core risk management system for the trading bot.
    """
    
    def __init__(self, max_position_size: float = 0.1, stop_loss_pct: float = 0.02, 
                 take_profit_pct: float = 0.05, max_daily_loss: float = 0.05):
        """
        Initialize risk manager.
        
        Args:
            max_position_size: Maximum percentage of account to risk per trade (default 10%)
            stop_loss_pct: Stop loss percentage (default 2%)
            take_profit_pct: Take profit percentage (default 5%)
            max_daily_loss: Maximum daily loss percentage (default 5%)
        """
        self.max_position_size = max_position_size
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.max_daily_loss = max_daily_loss
        
    def calculate_position_size(self, account_balance: float, entry_price: float, 
                               stop_loss_distance: float) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            account_balance: Current account balance
            entry_price: Entry price of the trade
            stop_loss_distance: Distance to stop loss
            
        Returns:
            Position size in contracts
        """
        try:
            # Risk per trade = account_balance * max_position_size
            risk_amount = account_balance * self.max_position_size
            
            # Calculate position size (simplified)
            position_size = risk_amount / (entry_price * stop_loss_distance)
            
            logger.debug(f"Calculated position size: {position_size}")
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return 0.0
    
    def check_stop_loss(self, current_price: float, entry_price: float, 
                       stop_loss_pct: Optional[float] = None) -> bool:
        """
        Check if stop loss is triggered.
        
        Args:
            current_price: Current price
            entry_price: Entry price
            stop_loss_pct: Stop loss percentage (uses default if not specified)
            
        Returns:
            True if stop loss is triggered, False otherwise
        """
        try:
            sl_pct = stop_loss_pct if stop_loss_pct is not None else self.stop_loss_pct
            
            # Calculate stop loss price based on trade type
            if current_price <= entry_price * (1 - sl_pct):
                logger.info(f"Stop loss triggered at {current_price}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking stop loss: {e}")
            return False
    
    def check_take_profit(self, current_price: float, entry_price: float, 
                         take_profit_pct: Optional[float] = None) -> bool:
        """
        Check if take profit is triggered.
        
        Args:
            current_price: Current price
            entry_price: Entry price
            take_profit_pct: Take profit percentage (uses default if not specified)
            
        Returns:
            True if take profit is triggered, False otherwise
        """
        try:
            tp_pct = take_profit_pct if take_profit_pct is not None else self.take_profit_pct
            
            # Calculate take profit price based on trade type
            if current_price >= entry_price * (1 + tp_pct):
                logger.info(f"Take profit triggered at {current_price}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking take profit: {e}")
            return False
    
    def enforce_kill_switch(self, account_balance: float, initial_balance: float) -> bool:
        """
        Check if kill switch should be activated (account balance dropped too much).
        
        Args:
            account_balance: Current account balance
            initial_balance: Initial account balance
            
        Returns:
            True if kill switch is activated, False otherwise
        """
        try:
            loss_pct = (initial_balance - account_balance) / initial_balance
            
            if loss_pct >= self.max_daily_loss:
                logger.warning(f"Kill switch activated. Loss percentage: {loss_pct:.2%}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking kill switch: {e}")
            return False