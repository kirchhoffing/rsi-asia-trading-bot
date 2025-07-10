#!/usr/bin/env python3
"""
Main entry point for the RSI Divergence Crypto Trading Bot.
Handles configuration validation, strategy execution, and scheduling.
"""

import signal
import sys
import time
from datetime import datetime
import schedule

from src.config import config
from src.logger import logger
from src.trading_strategy import RSIDivergenceStrategy

class TradingBot:
    """Main trading bot class that orchestrates the entire system."""
    
    def __init__(self):
        self.strategy = None
        self.is_running = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.is_running = False
        if self.strategy:
            self.strategy.shutdown()
        sys.exit(0)
    
    def validate_configuration(self) -> bool:
        """Validate bot configuration before starting."""
        logger.logger.info("Validating configuration...")
        
        validation_result = config.validate_config()
        
        # Log warnings
        for warning in validation_result['warnings']:
            logger.logger.warning(warning)
        
        # Log errors
        for error in validation_result['errors']:
            logger.logger.error(error)
        
        if not validation_result['valid']:
            logger.logger.error("Configuration validation failed. Please fix the errors above.")
            return False
        
        logger.logger.info("Configuration validation successful!")
        return True
    
    def run_strategy_cycle(self):
        """Run one cycle of the trading strategy."""
        try:
            logger.logger.info(f"Starting strategy cycle at {datetime.now()}")
            
            if not self.strategy:
                self.strategy = RSIDivergenceStrategy()
            
            # Execute the strategy
            self.strategy.execute_strategy()
            
            logger.logger.info("Strategy cycle completed successfully")
            
        except Exception as e:
            logger.log_error(e, "Error in strategy cycle")
    
    def run_continuous(self):
        """Run the bot continuously with scheduling."""
        logger.logger.info("Starting continuous trading bot...")
        
        # Schedule strategy execution every hour
        schedule.every().hour.do(self.run_strategy_cycle)
        
        # Also run immediately on startup
        self.run_strategy_cycle()
        
        self.is_running = True
        
        while self.is_running:
            try:
                # Check for scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                logger.log_error(e, "Error in main loop")
                time.sleep(60)  # Wait before retrying
    
    def run_once(self):
        """Run the strategy once and exit."""
        logger.logger.info("Running strategy once...")
        
        try:
            self.strategy = RSIDivergenceStrategy()
            self.strategy.execute_strategy()
            
            logger.logger.info("Single run completed successfully")
            
        except Exception as e:
            logger.log_error(e, "Error in single run")
        finally:
            if self.strategy:
                self.strategy.shutdown()
    
    def display_help(self):
        """Display help information."""
        help_text = """
RSI Divergence Crypto Trading Bot

Usage: python main.py [options]

Options:
  --once        Run the strategy once and exit
  --continuous  Run continuously with hourly scheduling (default)
  --help        Display this help message

Configuration:
  Copy env.example to .env and configure your settings
  
  Key settings:
  - EXCHANGE_NAME: Exchange to use (binance, etc.)
  - API_KEY/API_SECRET: Exchange API credentials
  - TRADING_PAIRS: Comma-separated list of pairs to trade
  - SIMULATE_TRADING: Set to True for simulation mode
  
Examples:
  python main.py --once           # Run once
  python main.py --continuous     # Run continuously
  python main.py                  # Run continuously (default)
"""
        print(help_text)

def main():
    """Main function."""
    bot = TradingBot()
    
    # Parse command line arguments
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        bot.display_help()
        return
    
    # Validate configuration
    if not bot.validate_configuration():
        return
    
    # Determine run mode
    if '--once' in args:
        bot.run_once()
    else:
        # Default to continuous mode
        bot.run_continuous()

if __name__ == "__main__":
    main() 