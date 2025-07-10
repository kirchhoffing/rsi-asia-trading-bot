"""
Logging configuration module for the RSI Divergence Trading Bot.
Provides structured logging with file output and console display.
"""

import logging
import os
from datetime import datetime
from typing import Optional

from .config import config

class TradingLogger:
    """Trading bot logger with file and console output."""
    
    def __init__(self, name: str = "RSI_Trading_Bot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure formatters
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Setup handlers
        self._setup_file_handler()
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """Setup file handler for logging."""
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.file_formatter)
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """Setup console handler for logging."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_trade_signal(self, pair: str, signal: str, price: float, rsi: float, 
                        divergence_strength: Optional[float] = None):
        """Log trading signal with structured format."""
        message = f"SIGNAL: {signal} | {pair} | Price: {price:.4f} | RSI: {rsi:.2f}"
        if divergence_strength:
            message += f" | Divergence: {divergence_strength:.2f}"
        
        self.logger.info(message)
    
    def log_order_execution(self, order_type: str, pair: str, amount: float, 
                           price: float, order_id: Optional[str] = None):
        """Log order execution details."""
        message = f"ORDER: {order_type} | {pair} | Amount: {amount:.6f} | Price: {price:.4f}"
        if order_id:
            message += f" | ID: {order_id}"
        
        self.logger.info(message)
    
    def log_position_update(self, pair: str, position_size: float, 
                           unrealized_pnl: float, realized_pnl: float):
        """Log position update information."""
        message = f"POSITION: {pair} | Size: {position_size:.6f} | Unrealized PnL: {unrealized_pnl:.4f} | Realized PnL: {realized_pnl:.4f}"
        self.logger.info(message)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context information."""
        message = f"ERROR: {context} | {str(error)}"
        self.logger.error(message, exc_info=True)
    
    def log_startup(self, mode: str = "simulation"):
        """Log bot startup information."""
        self.logger.info(f"=== RSI Divergence Trading Bot Started ===")
        self.logger.info(f"Mode: {mode.upper()}")
        self.logger.info(f"Exchange: {config.EXCHANGE_NAME}")
        self.logger.info(f"Trading Pairs: {', '.join(config.TRADING_PAIRS)}")
        self.logger.info(f"RSI Period: {config.RSI_PERIOD}")
        self.logger.info(f"RSI Thresholds: {config.RSI_OVERSOLD}/{config.RSI_OVERBOUGHT}")
    
    def log_shutdown(self):
        """Log bot shutdown information."""
        self.logger.info("=== RSI Divergence Trading Bot Shutdown ===")

# Create global logger instance
logger = TradingLogger() 